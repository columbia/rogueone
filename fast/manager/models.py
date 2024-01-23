import csv
import enum
import json
from pathlib import Path
from typing import List, Any, Tuple, Set
from typing import Optional
import celery
import dateutil.rrule
import sqlalchemy
from sqlalchemy import String, DateTime, func, Integer, JSON, Float, Boolean, Table, Column
from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.event import listens_for
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, declared_attr, Session
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import ColumnOperators
import fast.dataflow.cross_package as cp
from datetime import timedelta, datetime
import os
import sys
import subprocess
import re
import fast.manager.registry
from enum import Enum

PATH_MAX = 4096
d2h_js_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                            '../esprima-csv/diff2json.js'))
core_groups = ['BenignSamples', 'BenignSamples2', 'RandomBenignSamples', 'RandomBenignSamples2',
              '30_backstabber_samples', 'checkmarks_stabber_samples', 'new_backstabber_samples',
              'amalfi_NPM']
rejected_vps = [35578, 1199]

analysis_cutoff = datetime(2023, 11, 24, 0, 0)

@declarative_mixin
class Common:
    """Common functionality shared between all declarative models."""
    __abstract__ = True
    __name__: str
    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(), default=func.now())
    """Date/time of instance creation."""
    updated_at: Mapped[DateTime] = mapped_column(DateTime(), default=func.now())
    """Date/time of instance last update."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Base(Common, DeclarativeBase):
    pass


class Package(Base):
    name: Mapped[str] = mapped_column(String(214), unique=True)
    author_name: Mapped[str] = mapped_column(String(300), nullable=True)
    author_email: Mapped[str] = mapped_column(String(300), nullable=True)
    author_url: Mapped[str] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)  # Truncate to first thousand chars

    # dependents: Mapped[int] = mapped_column(INT)
    versions: Mapped[List["Version"]] = relationship(back_populates="package", cascade='delete')

    has_timeout: Mapped[bool] = mapped_column(Boolean, server_default='false', default=False)

    def __repr__(self):
        return f"<P {self.id}: {self.name} { 'has a timeout' if self.has_timeout else ''}>"


class DependentDependency(Base):
    __table_args__ = tuple(
        UniqueConstraint("dependent_id", "dependency_id"),
    )
    dependent_id: Mapped[int] = mapped_column(ForeignKey('version' + '.id'))
    dependency_id: Mapped[int] = mapped_column(ForeignKey('version' + '.id'))
    dependent: Mapped["Version"] = relationship("Version",foreign_keys=[dependent_id])
    dependency: Mapped["Version"] = relationship("Version",foreign_keys=[dependency_id])
    transitive: Mapped[bool] = mapped_column(sqlalchemy.Boolean, nullable=True)

class Version(Base):
    __table_args__ = tuple(
        UniqueConstraint("package_id", "number"),
    )
    number: Mapped[str] = mapped_column(String(256))
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    disk_location: Mapped[str] = mapped_column(String(PATH_MAX), nullable=True, unique=True)  # Dummy Versions
    package_id: Mapped[int] = mapped_column(ForeignKey(Package.__tablename__ + '.id'))
    package: Mapped[List["Package"]] = relationship(back_populates="versions")
    package_json: Mapped[JSON] = mapped_column(JSON, nullable=True)

    downloads: Mapped[int] = mapped_column(Integer, nullable=True) # Maybe this needs to be BigInt
    dependencies_assoc: Mapped[List["DependentDependency"]] = relationship(back_populates='dependent', foreign_keys=[DependentDependency.dependent_id])
    dependents_assoc: Mapped[List["DependentDependency"]] = relationship(back_populates='dependency', foreign_keys=[DependentDependency.dependency_id])
    dependencies: Mapped[List["Version"]] = relationship("Version", secondary=DependentDependency.__tablename__, viewonly=True, primaryjoin="Version.id == DependentDependency.dependent_id", secondaryjoin="Version.id==DependentDependency.dependency_id")
    dependents: Mapped[List["Version"]] = relationship("Version", secondary=DependentDependency.__tablename__, viewonly=True, primaryjoin="Version.id == DependentDependency.dependency_id", secondaryjoin="Version.id==DependentDependency.dependent_id")
    analysis_results: Mapped[List["TaskModel"]] = relationship("TaskModel", back_populates="version")
    #dependents: Mapped[List["Version"]] = relationship("Version", secondary=DependentDependency.__tablename__, foreign_keys=[DependentDependency.dependency_id], back_populates='dependencies', viewonly=True, primaryjoin='DependentDependency.dependency_id == Version.id', remote_side='DependentDependency.dependent_id')
    # Gets the full dependency list of a version.

    def name_for_npm(self):
        if '@' in self.package.name:
            s = self.package.name.split('@')
            if len(s) == 2:
                user, pname = s
            elif len(s) == 3:
                _, user, pname = s
            return f"@{user}/{pname}"
        else:
            return self.package.name

    def __repr__(self):
        return f"<V {self.id}: {self.package.name if self.package else '?'}@{self.number}>"
    def get_dependencies(self):
        name = self.name_for_npm()
        return fast.manager.registry.fetch_version_dependencies(name, self.number, str(Path(self.disk_location) / 'package.json'))

    def save_dependencies(self, session, deps: list[str]):
        if not deps:
            sys.stderr.write(f"Saving no deps for {self}.\n")
            return []
        split_deps = [d.rsplit("@", 1) for d in deps if d]
        dep_rels = []
        new_vs = []
        for package_s, version_s in split_deps:
            p = get_or_create(session, Package, name=package_s )[0]
            v, is_new_v = get_or_create(session, Version, package_id=p.id, number=version_s)
            rel = DependentDependency(dependent_id=self.id, dependency_id = v.id)
            dep_rels.append(rel)
            session.add(rel)
            if is_new_v:
                new_vs.append(v)
        #existing_deps = session.query(Version).join(Package).filter((Package.name + '@' + Version.number).in_(deps)).all()
        session.add(self)
        return new_vs

    def dependency_cache_path(self):
        return Path(self.disk_location) / '__rogue_one_dependency_cache.json'
    def get_cached_dependencies(self) -> tuple[bool, Optional[list]]:
        p = self.dependency_cache_path()
        if not p.exists():
            return False, None
        with open(p) as f:
            return True, json.load(f)

    def save_dependencies_to_cache(self, data):
        with open(self.dependency_cache_path(), 'w') as f:
            json.dump(data, f)
    # Gets the full dependency list of a version and saves it to the database
    def create_dependencies(self, session, cache=True):
        if cache:
            cached, res = self.get_cached_dependencies()
            if cached:
                return self.save_dependencies(session, res)
        deps = self.get_dependencies()
        res = self.save_dependencies(session, deps)
        self.save_dependencies_to_cache(deps)
        return res
    def dependency_analysis_results_query(self, session):
        q = session.query(Package.name, TaskModel.state,
                                 TaskModel.run_timestamp,
                              sqlalchemy.func.json_object_keys(
                                  sqlalchemy.func.coalesce(TaskModel.json_result['rels'], '{"": null}')
                              )
                          ).\
            join(TaskModel.version).\
            join(Package, Version.package_id == Package.id).\
            join(Version.dependents_assoc).\
                filter(DependentDependency.dependent_id == self.id).\
                filter(TaskModel.state == State.CompletedSuccess).\
                filter(TaskModel.run_timestamp > analysis_cutoff)
        return q
    #q = session.query(Package.name, TaskModel.state, TaskModel.run_timestamp, TaskModel.json_result['rels']).join(TaskModel.version, TaskModel.version_id == Version.id).join(Package, Version.package_id == Package.id).join(Version.dependents_assoc).filter(DependentDependency.dependent_id == self.id).filter(TaskModel.state == State.CompletedSuccess)

    def dependency_analysis_results(self, session):
        tm_rels = self.dependency_analysis_results_query(session).all()
        all_deps = session.query(Package.name).join(Version.dependents_assoc).join(Version.package).\
            filter(DependentDependency.dependent_id == self.id)
        dep_names = [v[0] for v in all_deps]

        results = {
            'data': {}, # Map from dep name to results
            'error_dependencies': set(),
            'not_included_dependencies': set(dep_names),# list of dep names
            'analysis_timestamps': {} # map from dep name to datetime
        }
        
        for tm in tm_rels:
            tm: tuple
            p_name, tm_state, tm_timestamp, tm_rel = tm
            # Need tm.state, p.name, tm.run_timestamp, tm.json_result['rels']
            if tm_rels != '':
                if p_name not in results['data'] or tm_timestamp > results['analysis_timestamps'][p_name]:
                    results['data'][p_name] = {tm_rel: []}
                    results['analysis_timestamps'][p_name] = tm_timestamp
                elif tm_timestamp == results['analysis_timestamps'][p_name]:
                    results['data'][p_name][tm_rel] = []
                for s in (results['error_dependencies'], results['not_included_dependencies']):
                    if p_name in s:
                        s.remove(p_name)
        results['not_included_dependencies'] = list(results['not_included_dependencies'])
        return results
    
    def q_without_completed_analysis(session):
        dep_query = session.query(Version).join(Version.dependents_assoc)
        dep_query = dep_query.outerjoin(TaskModel,
                                        sqlalchemy.and_(TaskModel.version_id == Version.id,
                                                        TaskModel.state == State.CompletedSuccess))
        dep_query = dep_query.filter(TaskModel.id == None)

        return dep_query

    def q_core_without_completed_analysis(session):
        q = Version.q_without_completed_analysis(session)
        q = q.join(VersionPair, sqlalchemy.and_(sqlalchemy.or_(VersionPair.before_id == Version.id,
                                               VersionPair.after_id == Version.id), VersionPair.group.in_(core_groups)))
        return q

class State(Enum):
    # Task needs to be done, but has not started by a worker.
    NotStarted = 1
    # Task has picked up by a celery worker, and may or not still be running,
    # if an error occurred that killed the worker process
    Running = 2
    # Task has been completed with no error
    CompletedSuccess = 3
    # Task has been completed with an error
    CompletedError = 4
    ExceptionCaught = 5
    TimedOut = 6

class VersionPair(Base):
    before_id: Mapped[int] = mapped_column(ForeignKey(Version.__tablename__ + '.id'))
    after_id: Mapped[int] = mapped_column(ForeignKey(Version.__tablename__ + '.id'))
    before: Mapped["Version"] = relationship(foreign_keys=[before_id])
    after: Mapped["Version"] = relationship(foreign_keys=[after_id])

    label: Mapped[str] = mapped_column(String(32))
    human_label: Mapped[str] = mapped_column(String(32), nullable=True)
    group: Mapped[str] = mapped_column(String(128))
    disk_location: Mapped[str] = mapped_column(String(PATH_MAX), unique=True)

    diff_json: Mapped[JSON] = mapped_column(JSON)

    rogue_one_results: Mapped[List["RogueOneResult"]] = relationship(cascade='delete')
    version_pair_task_models: Mapped[List["VersionPairTaskModel"]] = relationship(cascade='delete')
    
    # Record whether the dependencies of a VersionPair's versions have been retreived
    deps_download_state: Mapped[State] = mapped_column(sqlalchemy.Enum(State),
            server_default=State.NotStarted.name)
    # Single package (old style) analysis
    ignore: Mapped[bool] = mapped_column(Boolean, server_default="f")
    def __repr__(self):
        return f"<VP {self.id}: {self.before.package.name if self.before and self.before.package else '?'} {self.before.number}-->{self.after.number}>"

    def update_diff_json(self):
        before = self.before
        after = self.after
        if not before or not after:
            sys.stderr.write(f"Somehow {self.id} does not have a before or an after version.\n")
            self.diff_json = {'error': 'versions not saved'}
            return
        package_name = self.before.package.name

        try:
            diff_cmd = [
                "diff", "-r", "-u","-bZE", "--unidirectional-new-file",
                "--exclude=*.log", "--exclude=*.gexf", "--exclude=odgen*.json", "--exclude=fast*.json",
                "--exclude=*.csv",
                "--exclude=*.tsv", "--exclude=*.ndjson",
                before.disk_location,
                after.disk_location,
            ]
            diff_output_processing_command = [
                "node", d2h_js_path,
            ]
            diff_p = subprocess.Popen(diff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            diff_processor_p = subprocess.Popen(diff_output_processing_command, stdin=diff_p.stdout,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            diff_json = diff_processor_p.communicate()[0]
        except celery.exceptions.SoftTimeLimitExceeded as e:
            raise e
        except Exception as e:
            sys.stderr.write(f"Failed to build diff json for {package_name}, {self.disk_location}, {e}.\n")
            self.diff_json = {"error": "diff process failed"}
            return False
        self.diff_json = diff_json
        return True

    def cross_package_analysis_data(self, session) -> dict:
        deps = Version.__table__.alias(name='v_deps')
        result = {
            'package_name': self.before.package.name,
            'before_number': self.before.number,
            'after_number': self.after.number,
        }
        # A version pair is ready for cross package analysis if:
        # For both of vp.before, vp.after:
        #   The dependency list was successfully downloaded
        #   All dependencies were successfully analyzed
        if self.deps_download_state != State.CompletedSuccess:
            return {'error': 'download not completed'}
        for k, v in (('before', self.before), ('after', self.after)):
            v_result = {}
            result[k] = v.dependency_analysis_results(session)
        return result

    def cross_package_new_reachables(self, session, ror=None) -> Optional[tuple[set, set]]:
        if self.deps_download_state != State.CompletedSuccess:
            return None
        if not ror:
            ror = self.most_recent_ror(session)
        data = self.cross_package_analysis_data(session)
        p_name = self.before.package.name
        if ror and 'system_extra_info' in ror.json_result and 'before_rels' in ror.json_result['system_extra_info'] and 'after_rels' in ror.json_result['system_extra_info']:
            for s in ('before', 'after'):
                rels = ror.json_result['system_extra_info'][f"{s}_rels"]
                data[s]['data'][p_name] = rels
                if p_name in data[s]['not_included_dependencies']:
                    data[s]['not_included_dependencies'].remove(p_name)
        #from pprint import pp
        #pp(list(data['before']['data'][p_name].keys()))
        #pp(list(data['after']['data'][p_name].keys()))

        bg, ag = cp.graphs_from_version_pair_data(data)
        if not bg or not ag:
            sys.stderr.write(f"No graph present for cross package analysis for {self.__repr__()}\n")
            return None
        static_diff, user_diff = cp.graph_differences(bg, ag, data)
        return static_diff, user_diff


    def csv_line(self, session)-> Optional[list]:
        #csv_header = ['label', 'package_name', 'group', 'system',
        # 'run_timestamp', 'before_weakly_connected_components', 'v_id', 'sinks_changed',
        # 'before_version', 'after_version',
        # 'suspicious_paranoid','suspicious_p_filtered',
        # 'before_running_time', 'after_running_time', 'before_error', 'after_error',
        # 'suspicious', 'system_extra_info']

        # First try to find a successful analysis:
        base_q = session.query(RogueOneResult).join(VersionPair).filter(VersionPair.id == self.id) 
        base_q = base_q.order_by(RogueOneResult.run_timestamp.desc())
        base_q = base_q.filter(RogueOneResult.run_timestamp > analysis_cutoff)
        ror_q = base_q.filter(RogueOneResult.error == 'OK')
        ror = ror_q.first()
        if not ror:
            ror = base_q.first()

        if not ror:
            return [
                self.label, self.before.package.name, self.group, 'rogue_one',
                None, None, None, self.id,
                self.before.number, self.after.number,
                None, None,
                None, None, 'No completed analysis.', 'No completed analysis.',
                False,None 
            ]

        b = 'before'
        a = 'after'
        try:
            before_running_time = ror.json_result[b]['running_time']
            after_running_time = ror.json_result[a]['running_time']
            before_error = ror.json_result[b]['error']
            after_error = ror.json_result[a]['error']
        except:
            before_running_time = None
            after_running_time = None
            before_error = None
            after_error = None

        sei = {}
        if 'system_extra_info' in ror.json_result:
            if type(ror.json_result['system_extra_info']) == str:
                sei = ror.json_result['system_extra_info']
            else:
                for k in ror.json_result['system_extra_info']:
                    if 'code_locs' in k:
                        pass
                    elif '_rels' in k and type(ror.json_result['system_extra_info'][k]) == dict:
                        rel_map:dict[str, list[list[str]]] = ror.json_result['system_extra_info'][k]
                        sei[k] = list(set(rel_map.keys()))
                    else:
                        sei[k] = ror.json_result['system_extra_info'][k]

        def rel_has_dollar_string(rel):
            for x in rel:
                if re.match(":local.*\$.*", x):
                    return True
            return False

        def result_obj_has_dollar(distinct_rels):
            for rel in distinct_rels:
                if rel_has_dollar_string(rel):
                    return True
            return False

        if 'system_extra_info' in ror.json_result and 'flagged_all_local_distinct' in ror.json_result['system_extra_info']:
            suspicious_paranoid  = ((ror.error == 'OK') and ror.json_result['system_extra_info']['flagged_all_local_distinct'] != [])
            suspicious_pfiltered = ((ror.error == 'OK') and result_obj_has_dollar(ror.json_result['system_extra_info']['flagged_all_local_distinct']))
        else:
            suspicious_paranoid  = None
            suspicious_pfiltered = None
        
        cpr = self.cross_package_new_reachables(session, ror=ror)
        static_cp, user_cp = cpr if cpr else (None, None)
        return [
            ror.version_pair.label, ror.version_pair.before.package.name, ror.version_pair.group, 'rogue_one',
            ror.run_timestamp, suspicious_paranoid, suspicious_pfiltered, ror.version_pair_id,
            ror.version_pair.before.number, ror.version_pair.after.number,
            len(static_cp) if static_cp is not None else None, len(user_cp) if user_cp is not None else None,
            before_running_time, after_running_time, before_error, after_error,
            ror.suspicious, sei
        ]

    def q_core_vps(session):
        return session.query(VersionPair).filter(VersionPair.group.in_(core_groups)).filter(sqlalchemy.not_(VersionPair.id.in_(rejected_vps)))

    def core_scripts(session):
        n = sqlalchemy.types.JSON.NULL
        vb = sqlalchemy.orm.aliased(Version)
        va = sqlalchemy.orm.aliased(Version)
        jb = sqlalchemy.dialects.postgresql.JSONB
        q = session.query(VersionPair.id, VersionPair.label, VersionPair.group, Package.name, vb.number, va.number, 
                vb.package_json['scripts']['preinstall'], 
                vb.package_json['scripts']['install'], 
                vb.package_json['scripts']['postinstall'], 
                va.package_json['scripts']['preinstall'], 
                va.package_json['scripts']['install'], 
                va.package_json['scripts']['postinstall'], 
            ).join(vb, vb.id == VersionPair.before_id).join(va, va.id == VersionPair.after_id
            ).join(Package, vb.package_id == Package.id
            ).filter(VersionPair.group.in_(core_groups)
                    ).filter(sqlalchemy.not_(VersionPair.id.in_(rejected_vps)))
        #q = q.filter(sqlalchemy.or_(vb.package_json.cast(jb).op('?')('scripts'), va.package_json.cast(jb).op('?')('scripts')))
        return q

    def q_to_csv(query, path):
        with open(path, 'w') as f:
            c = csv.writer(f)
            c.writerow(csv_header)
            for vp in query.all():
                line = vp.csv_line(query.session)
                if not line:
                    sys.stderr.write(f"No analysis present for vp {vp}\n")
                    continue
                c.writerow(line)

    def with_latest_ror(session, before_dt=None, after_dt=analysis_cutoff):
        ror_q = session.query(VersionPair, RogueOneResult)
        if before_dt:
            ror_q = ror_q.join(RogueOneResult, sqlalchemy.and_(VersionPair.id == RogueOneResult.version_pair_id, RogueOneResult.run_timestamp < before_dt))
        else:
            ror_q = ror_q.join(RogueOneResult, VersionPair.id == RogueOneResult.version_pair_id)
        ror_q = ror_q.order_by(VersionPair.id, RogueOneResult.run_timestamp.desc())
        ror_q = ror_q.filter(RogueOneResult.error == 'OK')
        ror_q = ror_q.filter(RogueOneResult.run_timestamp > after_dt)
        ror_q = ror_q.distinct(VersionPair.id)
        return ror_q
    
    def most_recent_ror(self, session):
        res = VersionPair.with_latest_ror(session).filter(VersionPair.id == self.id).one_or_none()
        if res:
            return res[1]
        return None

    def with_latest_task_result(session, after_dt=analysis_cutoff, before_dt=None):
        vptm_q = session.query(VersionPair, VersionPairTaskModel)
        if before_dt:
            vptm_q = vptm_q.join(VersionPairTaskModel, sqlalchemy.and_(VersionPair.id == VersionPairTaskModel.version_id,
                                                                     VersionPairTaskModel.run_timestamp < before_dt))
        else:
            vptm_q = vptm_q.join(VersionPairTaskModel, VersionPair.id == VersionPairTaskModel.version_id)
        vptm_q = vptm_q.order_by(VersionPair.id, VersionPairTaskModel.run_timestamp.desc())
        vptm_q = vptm_q.filter(VersionPairTaskModel.error == 'OK')
        vptm_q = vptm_q.filter(VersionPairTaskModel.run_timestamp > after_dt)
        vptm_q = vptm_q.distinct(VersionPair.id)
        return vptm_q


    def most_recent_task_result(self, session, after_dt=analysis_cutoff):
        res = VersionPair.with_latest_task_result(session, after_dt=after_dt).filter(VersionPair.id == self.id).one_or_none()
        if res:
            return res[1]
        return None

    def q_survey_between_dates(session, start, end):
        return session.query(VersionPair).join(VersionPair.rogue_one_results).order_by(VersionPair.id, RogueOneResult.run_timestamp.desc()).distinct(VersionPair.id).filter(VersionPair.group == 'active_survey').filter(RogueOneResult.run_timestamp > start).filter(RogueOneResult.run_timestamp < end)

    def retro_survey_vptms(session):
        q = session.query(VersionPairTaskModel).join(VersionPair).where(VersionPair.group == 'retro_survey').where(VersionPairTaskModel.state != State.NotStarted).order_by(VersionPairTaskModel.run_timestamp.desc())
        best_results = {}
        for vptm in q:
            vpid = vptm.version_id
            if vpid not in best_results:
                best_results[vpid] = vptm
            else:
                cur = best_results[vpid]
                if vptm.state == State.CompletedSuccess and cur.state != State.CompletedSuccess:
                    best_results[vpid] = vptm
                elif cur.state == State.Running and vptm.state != State.Running:
                    best_results[vpid] = vptm

        brl = list(best_results.values())
        csv_list = [
                ['system', 'group', 'package_name', 'run_timestamp', 'suspicious', 'suspicious_paranoid', 'human_label', 
                  'version_pair_db_id', 'before_version', 'after_version',
                  'error','state',
                  'before_running_time', 'after_running_time', 'total_running_time', 'rss_mem','ast_nodes',
                  'before_odg_nodes', 'before_odg_edges',
                  'before_odrg_nodes', 'before_odrg_edges',
                  'after_odg_nodes', 'after_odg_edges',
                  'after_odrg_nodes', 'after_odrg_edges',
                'vptm_db_id']
                ]
        for vptm in brl:
            vp = vptm.version_pair
            try:
                before_running_time = vptm.json_result.get('before',{}).get('running_time', None)
                after_running_time = vptm.json_result.get('after',{}).get('running_time', None)
            except:
                before_running_time = None
                after_running_time = None
            try:
                sus = vptm.json_result.get('suspicious', False)
            except:
                sus = False
            try:
                if 'system_extra_info' in vptm.json_result and 'flagged_all_local_distinct' in vptm.json_result['system_extra_info']:
                    suspicious_paranoid  = ((vptm.ervptm == 'OK') and vptm.json_result['system_extra_info']['flagged_all_local_distinct'] != [])
                else:
                    suspicious_paranoid  = None
            except:
                suspicious_paranoid = None
            try:
                rss_mem = vptm.json_result.get('system_extra_info', {}).get('mem_info', {}).get('rss', None)
            except:
                rss_mem = None
            try:
                sei = str(vptm.json_result['system_extra_info'])[0:10000]
            except:
                sei = ''
            try:
                ast_nodes = sum(vptm.json_result['before']['file_node_nums'].values())
                ast_nodes = ast_nodes + sum(vptm.json_result['after']['file_node_nums'].values())
                if ast_nodes == 0:
                    ast_nodes = None
            except:
                ast_nodes = None
            
            
            before_odg_nodes = before_odg_edges = before_odrg_nodes = before_odrg_edges = None
            after_odg_nodes = after_odg_edges = after_odrg_nodes = after_odrg_edges = None
            try:
                before_odg_nodes = vptm.json_result['before']['graph_size']['odg']['nodes']
                before_odg_edges= vptm.json_result['before']['graph_size']['odg']['edges']
                before_odrg_nodes= vptm.json_result['before']['graph_size']['idg']['nodes']
                before_odrg_edges= vptm.json_result['before']['graph_size']['idg']['edges']
                after_odg_nodes = vptm.json_result['after']['graph_size']['odg']['nodes']
                after_odg_edges= vptm.json_result['after']['graph_size']['odg']['edges']
                after_odrg_nodes= vptm.json_result['after']['graph_size']['idg']['nodes']
                after_odrg_edges= vptm.json_result['after']['graph_size']['idg']['edges']
            except:
                pass

            csv_list.append(
                [ 'rogue_one', vp.group, vp.before.package.name, vptm.run_timestamp, sus, suspicious_paranoid, vp.human_label, vptm.version_id,
                    vp.before.number, vp.after.number,
                    vptm.error,vptm.state,
                    before_running_time, after_running_time, vptm.analysis_length,rss_mem,ast_nodes,
                    before_odg_nodes, before_odg_edges, before_odrg_nodes, before_odrg_edges,
                    after_odg_nodes, after_odg_edges, after_odrg_nodes, after_odrg_edges,
                    vptm.id
                ]
                )
        return csv_list

    def survey_csv_line(self, session):
        base_q = session.query(VersionPairTaskModel).join(VersionPair).filter(VersionPair.id == self.id) 
        base_q = base_q.order_by(VersionPairTaskModel.run_timestamp.desc())
        base_q = base_q.filter(VersionPairTaskModel.run_timestamp > analysis_cutoff)
        ror_q = base_q.filter(VersionPairTaskModel.error == 'OK')
        ror = ror_q.first()
        if not ror:
            ror = base_q.first()

        if not ror:
            return [
                self.label, self.before.package.name, self.group, 'rogue_one',
                None, None, None, self.id,
                self.before.number, self.after.number,
                None, None,
                None, None, 'No completed analysis.', 'No completed analysis.',
                False,None 
            ]

        b = 'before'
        a = 'after'
        try:
            before_running_time = ror.json_result[b]['running_time']
            after_running_time = ror.json_result[a]['running_time']
            before_error = ror.json_result[b]['error']
            after_error = ror.json_result[a]['error']
        except:
            before_running_time = None
            after_running_time = None
            before_error = None
            after_error = None

        sei = {}
        if 'system_extra_info' in ror.json_result:
            if type(ror.json_result['system_extra_info']) == str:
                sei = ror.json_result['system_extra_info']
            else:
                for k in ror.json_result['system_extra_info']:
                    if 'code_locs' in k:
                        pass
                    elif '_rels' in k and type(ror.json_result['system_extra_info'][k]) == dict:
                        rel_map:dict[str, list[list[str]]] = ror.json_result['system_extra_info'][k]
                        sei[k] = list(set(rel_map.keys()))
                    else:
                        sei[k] = ror.json_result['system_extra_info'][k]


        if 'system_extra_info' in ror.json_result and 'flagged_all_local_distinct' in ror.json_result['system_extra_info']:
            suspicious_paranoid  = ((ror.error == 'OK') and ror.json_result['system_extra_info']['flagged_all_local_distinct'] != [])
        else:
            suspicious_paranoid  = None
        if type(ror.json_result) == str:
            sus = None
        else:
            sus = ror.json_result.get('suspicious')

        fast_mode = False
        if type(ror.json_result) != str:
            fast_mode = ror.json_result.get('fast_mode', False)
        
        cpr = self.cross_package_new_reachables(session, ror=ror)
        static_cp, user_cp = cpr if cpr else (None, None)
        return [ 'rogue_one', self.group, self.before.package.name, ror.run_timestamp, sus, suspicious_paranoid, self.human_label, ror.version_id,
            ror.version_pair.before.number, ror.version_pair.after.number,
            len(static_cp) if static_cp is not None else None, len(user_cp) if user_cp is not None else None,
            before_running_time, after_running_time, before_error, after_error,
            fast_mode, ror.id,
            sei
        ]

    survey_csv_header = ['system', 'group', 'package_name', 'run_timestamp', 'suspicious', 'suspicious_paranoid', 'human_label', 
                  'version_pair_db_id', 'before_version', 'after_version',
                  'static_cross_p_new_reachables', 'user_cross_p_new_reachables',
                  'before_running_time', 'after_running_time', 'before_error', 'after_error', 
                  'fast_mode', 'vptm_db_id', 'system_extra_info']

    def core_to_csv(session, path):
        query = VersionPair.q_core_vps(session)
        with open(path, 'w') as f:
            c = csv.writer(f)
            
            c.writerow(VersionPair.survey_csv_header)
            for vp in query.all():
                line = vp.survey_csv_line(query.session)
                if not line:
                    sys.stderr.write(f"No analysis present for vp {vp}\n")
                    continue
                c.writerow(line)
        

    def survey_to_csv(session, path, start, end):
        query = VersionPair.q_survey_between_dates(session, start, end)
        with open(path, 'w') as f:
            c = csv.writer(f)
            
            c.writerow(VersionPair.survey_csv_header)
            for vp in query.all():
                line = vp.survey_csv_line(query.session)
                if not line:
                    sys.stderr.write(f"No analysis present for vp {vp}\n")
                    continue
                c.writerow(line)


class TaskModel(Base):
    __table_args__ = tuple(
        UniqueConstraint("disk_location")
    )

    state: Mapped[State] = mapped_column(sqlalchemy.Enum(State), default=State.NotStarted)
    last_state_transition: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    def set_state(self, new_state: State):
        if self.state == State.Running:
            self.run_timestamp = self.last_state_transition
        self.state = new_state
        self.last_state_transition = datetime.now()

    def timed_out_tasks(session):
        now = datetime.now()
        return session.query(TaskModel).\
            filter(TaskModel.state == State.Running). \
            filter((now - TaskModel.last_state_transition) > text("interval '1 second' * timeout")).\
            all()
        #  Idk if theres a better way to do this.

    version_id: Mapped[int] = mapped_column(ForeignKey(Version.__tablename__ + '.id'))
    version: Mapped["Version"] = relationship()

    timeout: Mapped[int] = mapped_column(Integer)
    # version_date_random_slug
    disk_location: Mapped[str] = mapped_column(String(PATH_MAX), nullable=True)
    error: Mapped[str] = mapped_column(String(256), nullable=True)
    analysis_length: Mapped[Float] = mapped_column(Float, nullable=True)
    run_timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    json_result: Mapped[JSON] = mapped_column(JSON, nullable=True)
    num_retries: Mapped[Integer] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f"<TM {self.id}: {self.version.package.name if self.version else '?'}@{self.version.number} {self.state}>"
    def is_timed_out(self) -> bool:
        return (datetime.now() - self.last_state_transition) > timedelta(seconds=self.timeout)

class VersionPairTaskModel(Base):
    __table_args__ = tuple(
        UniqueConstraint("disk_location")
    )

    state: Mapped[State] = mapped_column(sqlalchemy.Enum(State), default=State.NotStarted)
    last_state_transition: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    def set_state(self, new_state: State):
        if self.state == State.Running:
            self.run_timestamp = self.last_state_transition
        self.state = new_state
        self.last_state_transition = datetime.now()

    def timed_out_tasks(session):
        now = datetime.now()
        return session.query(TaskModel). \
            filter(TaskModel.state == State.Running). \
            filter((now - TaskModel.last_state_transition) > text("interval '1 second' * timeout")). \
            all()
        #  Idk if theres a better way to do this.

    version_id: Mapped[int] = mapped_column(ForeignKey(VersionPair.__tablename__ + '.id'))
    version_pair: Mapped["VersionPair"] = relationship(back_populates="version_pair_task_models")

    timeout: Mapped[int] = mapped_column(Integer)
    error: Mapped[str] = mapped_column(String(256), nullable=True)
    analysis_length: Mapped[Float] = mapped_column(Float, nullable=True)
    run_timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    json_result: Mapped[JSON] = mapped_column(JSON, nullable=True)
    num_retries: Mapped[Integer] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f"<VPTM {self.id}: {self.version_pair.before.package.name if self.version_pair else '?'}@{self.version_pair.before.number} {self.state}>"

    def is_timed_out(self) -> bool:
        return self.state == State.Running and \
            (datetime.now() - self.last_state_transition) > timedelta(seconds=self.timeout)

    def flagged_rels_with_code_locs(self):
        sei = self.json_result['system_extra_info']
        rels = sei['new_rels']
        condensed_rels = dict()
        for k in sei['after_rels']:
            kp = re.sub("':local:[^']*'", "':local'", k)
            if kp not in condensed_rels:
                condensed_rels[kp] = sei['after_rels'][k]
            else:
                condensed_rels[kp].extend(sei['after_rels'][k])
        rels_with_nodes = [(r, condensed_rels[str(tuple(r))]) for r in rels if str(tuple(r)) in condensed_rels]
        rel_loc_map = dict()

        for r, node_pair_list in rels_with_nodes:
            r = tuple(r)
            if r not in rel_loc_map:
                rel_loc_map[r] = []
            for np in node_pair_list:
                a = sei['after_rel_code_locs'][np[0]]
                b = sei['after_rel_code_locs'][np[1]]
                rel_loc_map[r].append((a, b))
        return rel_loc_map


csv_header = ['label', 'package_name', 'group', 'system', 'run_timestamp',
               'suspicious_paranoid', 'suspicious_pfiltered',
              'version_pair_db_id', 'before_version', 'after_version',
              'static_cross_p_new_reachables', 'user_cross_p_new_reachables',
              'before_running_time', 'after_running_time', 'before_error', 'after_error', 'suspicious', 'system_extra_info']

class RogueOneResult(Base):
    __table_args__ = tuple(
        UniqueConstraint("run_timestamp", "disk_location"),
    )
    disk_location: Mapped[str] = mapped_column(String(PATH_MAX))
    error: Mapped[str] = mapped_column(String(256), nullable=True)
    analysis_length: Mapped[Float] = mapped_column(Float, nullable=True)
    run_timestamp: Mapped[DateTime] = mapped_column(DateTime)
    json_result: Mapped[JSON] = mapped_column(JSON)

    suspicious: Mapped[Boolean] = mapped_column(Boolean, nullable=True)

    before_weakly_connected_components: Mapped[int] = mapped_column(Integer, nullable=True)
    after_weakly_connected_components: Mapped[int] = mapped_column(Integer, nullable=True)
    callees_added = mapped_column(Integer, nullable=True)
    callees_removed = mapped_column(Integer, nullable=True)
    callees_changed = mapped_column(Integer, nullable=True)
    sinks_added = mapped_column(Integer, nullable=True)
    sinks_removed = mapped_column(Integer, nullable=True)
    sinks_changed = mapped_column(Integer, nullable=True)

    version_pair_id: Mapped[int] = mapped_column(ForeignKey(VersionPair.__tablename__ + '.id'))
    version_pair: Mapped["VersionPair"] = relationship(back_populates="rogue_one_results")

    def __repr__(self):
        return f"<ROR {self.id}: {self.version_pair} {self.error}, Sus: {self.suspicious}>"

    def processing_time(self):
        jr = self.json_result
        if 'system_extra_info' not in jr:
            return None
        sei = jr['system_extra_info']
        ppt = 'post_processing_time'
        brt = 'before_running_time'
        art = 'after_running_time'
        if brt not in sei or art not in sei or ppt not in sei:
            return None
        return RogueOneResult.parsetimedelta(sei[brt]) + RogueOneResult.parsetimedelta(sei[art]) + RogueOneResult.parsetimedelta(sei[ppt])
    def parsetimedelta(td_str):
        hour_s,min_s, sec_and_micros = td_str.split(':')
        sec_s, micro_s = sec_and_micros.split('.')
        hour = int(hour_s)
        minute = int(min_s)
        seconds = int(sec_s)
        micro = int(micro_s)
        return timedelta(hours=hour, minutes=minute, seconds=seconds,microseconds=micro)



    def flagged_rels_with_code_locs(self):
        sei = self.json_result['system_extra_info']
        rels = sei['new_rels']
        condensed_rels = dict()
        for k in sei['after_rels']:
            kp = re.sub("':local:[^']*'", "':local'", k)
            if kp not in condensed_rels:
                condensed_rels[kp] = sei['after_rels'][k]
            else:
                condensed_rels[kp].extend(sei['after_rels'][k])
        rels_with_nodes = [(r, condensed_rels[str(tuple(r))]) for r in rels if str(tuple(r)) in condensed_rels]
        rel_loc_map = dict()

        for r, node_pair_list in rels_with_nodes:
            r = tuple(r)
            if r not in rel_loc_map:
                rel_loc_map[r] = []
            for np in node_pair_list:
                a = sei['after_rel_code_locs'][np[0]]
                b = sei['after_rel_code_locs'][np[1]]
                rel_loc_map[r].append((a, b))
        return rel_loc_map

    def csv_line(self):
        #csv_header = ['label', 'package_name', 'group', 'system',
        # 'run_timestamp', 'sinks_added', 'sinks_removed', 'sinks_changed',
        # 'before_version', 'after_version',
        # 'before_weakly_connected_components', 'after_weakly_connected_components',
        # 'before_running_time', 'after_running_time', 'before_error', 'after_error',
        # 'suspicious', 'system_extra_info']
        b = 'before'
        a = 'after'
        try:
            before_running_time = self.json_result[b]['running_time']
            after_running_time = self.json_result[a]['running_time']
            before_error = self.json_result[b]['error']
            after_error = self.json_result[a]['error']
        except:
            before_running_time = None
            after_running_time = None
            before_error = None
            after_error = None

        sei = {}
        for k in self.json_result['system_extra_info']:
            if 'code_locs' in k:
                pass
            elif '_rels' in k and type(self.json_result['system_extra_info'][k]) == dict:
                rel_map:dict[str, list[list[str]]] = self.json_result['system_extra_info'][k]
                sei[k] = list(set(rel_map.keys()))
            else:
                sei[k] = self.json_result['system_extra_info'][k]
        return [
            self.version_pair.label, self.version_pair.before.package.name, self.version_pair.group, 'rogue_one',
            self.run_timestamp, self.sinks_added, self.sinks_removed, self.sinks_changed,
            self.version_pair.before.number, self.version_pair.after.number,
            self.before_weakly_connected_components, None,
            before_running_time, after_running_time, before_error, after_error,
            self.suspicious, sei
        ]


@listens_for(Session, "before_flush")
def updated_at_update(session: Session, param: Any, something: Any) -> None:
    """Set timestamp on update.

    Called from SQLAlchemy's
    [`before_flush`][sqlalchemy.orm.SessionEvents.before_flush] event to bump the `updated`
    timestamp on modified instances.

    Args:
        session: The sync [`Session`][sqlalchemy.orm.Session] instance that underlies the async
            session.
    """
    for instance in session.dirty:
        if hasattr(instance, "updated"):
            instance.updated = datetime.now()


# Cribbed from https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance, False
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)
        try:
            session.add(instance)

            session.commit()
        except celery.exceptions.SoftTimeLimitExceeded as e:
            raise e
        except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return instance, True
