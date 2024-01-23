import os
import sys
import json
from pprint import pp


from flask import Flask, render_template, url_for, redirect, request
from .engine import init
from .models import *
from sqlalchemy import text, select, literal_column, update, func, and_
from sqlalchemy.orm import joinedload, scoped_session
DL_THRESHOLD = 200

app = Flask(__name__, template_folder=os.path.realpath(os.path.join(os.path.dirname(__file__), "templates")))

db_file = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "db.json"))
if db_file:
    try:
        with open(db_file) as f:
            db = json.load(f)
    except FileNotFoundError as e:
        sys.stderr.write(f"No db config file found at {db_file}.\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Could not load json db config file at {db_file}.\n")
        sys.exit(1)
    db_uri = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
    engine, uSession = init(db_uri, echo=True)
else:
    engine, uSession = init(echo=False)
#session = Session()
Session = scoped_session(uSession)

@app.route('/')
def index():
    return redirect(url_for('report'))

@app.route('/versionpair/<int:id>')
def view_pair(id=None):
    id = int(id)
    session = Session()
    pair = session.query(VersionPair).filter_by(id=id).one()
    most_recent_result = session.query(VersionPairTaskModel).filter_by(version_id=pair.id).order_by(
        VersionPairTaskModel.run_timestamp.desc()).first()
    if not pair.diff_json:
        try:
            pair.update_diff_json()
            session.commit()
        except Exception as e:
            sys.stderr.write(f"Failed to update diff json for vp {id}: {e}.\n")
            pass
    try:
        rel_map = most_recent_result.flagged_rels_with_code_locs()
    except:
        rel_map = {}
    return render_template('versionpair.html', pair=pair,
            analysis_result=most_recent_result,
            rel_map=rel_map,
            cpnr=pair.cross_package_new_reachables(session))

@app.route('/report')
def report():
    data = {}
    # Packages downloaded
    session = Session()
    data['packages_downloaded'] = session.query(Package).count()
    # Version pairs downloaded
    data['pairs_downloaded'] = session.query(VersionPair).count()
    # Version pairs analyzed
    data['pairs_analyzed'] = session.query(VersionPair).join(VersionPairTaskModel
                                                             ).filter(VersionPairTaskModel.error == 'OK'
                                                             ).distinct(VersionPair.id
                                                             ).count()
    data['pairs_wcc_nonzero'] = 0
        # session.query(VersionPair).\
        # join(VersionPairTaskModel).filter(VersionPairTaskModel.error == 'OK').\
        # distinct(VersionPair.id).\
        # order_by(VersionPair.id, VersionPairTaskModel.run_timestamp.desc()).\
        # filter(VersionPairTaskModel.before_weakly_connected_components > 0).\
        # count()

    # Version pairs marked suspicious - any changes
    data['pairs_sus'] = session.query(VersionPair).\
        join(VersionPairTaskModel).filter(VersionPairTaskModel.error == 'OK').\
        distinct(VersionPair.id).\
        order_by(VersionPair.id, VersionPairTaskModel.run_timestamp.desc()).\
        filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).\
        count()

    data['pairs_sus_downloaded'] = session.query(VersionPair).\
        join(VersionPairTaskModel).filter(VersionPairTaskModel.error == 'OK').\
        join(VersionPair.before).filter(Version.downloads > DL_THRESHOLD).\
        filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).\
        distinct(VersionPair.id).\
        order_by(VersionPair.id, VersionPairTaskModel.run_timestamp.desc()).\
        count()
    
    sql = """
    SELECT x.VERSIONPAIRTASKMODEL_ERROR, count(x.VERSIONPAIRTASKMODEL_ERROR) FROM(
    SELECT DISTINCT ON (VERSIONPAIRTASKMODEL.VERSION_ID) VERSIONPAIRTASKMODEL.VERSION_ID AS VERSIONPAIRTASKMODEL_VERSION_ID,
	VERSIONPAIRTASKMODEL.ERROR AS VERSIONPAIRTASKMODEL_ERROR
    FROM VERSIONPAIRTASKMODEL
    ORDER BY VERSIONPAIRTASKMODEL.VERSION_ID,
	VERSIONPAIRTASKMODEL.RUN_TIMESTAMP DESC
	) x
    GROUP BY x.VERSIONPAIRTASKMODEL_ERROR
    """
    data['pairs_error_types'] = session.execute(text(sql)).all()


    v2 = Version.__table__.alias(name='after_version')
    sq = session.query(VersionPairTaskModel.version_id, func.max(VersionPairTaskModel.run_timestamp).label("max_rts")).group_by(VersionPairTaskModel.version_id).subquery()
    distinct_results =  session.query(Package.name,
                                      VersionPair.group,
                                      Version.number,
                                      literal_column('after_version.number'),
                                      func.to_char(VersionPairTaskModel.run_timestamp, 'DD Mon, HH24:MI:SS'),
                                      # VersionPairTaskModel.before_weakly_connected_components,
                                      # VersionPairTaskModel.after_weakly_connected_components,
                                      VersionPairTaskModel.error,
                                      VersionPairTaskModel.json_result['suspicious'].as_boolean(),
                                      VersionPairTaskModel.state,
                                      VersionPairTaskModel.version_id,
                                      VersionPairTaskModel.id
                                      ). \
        select_from(VersionPairTaskModel). \
        where(VersionPairTaskModel.run_timestamp != datetime.fromtimestamp(0)).\
        join(sq, and_(sq.c.version_id == VersionPairTaskModel.version_id, sq.c.max_rts == VersionPairTaskModel.run_timestamp)).\
        join(VersionPair, VersionPairTaskModel.version_pair).\
        join(Version, VersionPair.before).\
        join(Package, Version.package).\
        join(v2, VersionPair.after).\
        order_by(VersionPairTaskModel.run_timestamp.desc()).limit(1000)




    # data['distinct_table_cols'] = [
    #     'Package Name', 'Group', 'Before', 'After', 'Analysis Time',# 'Sinks +', 'Sinks Δ',
    #     'Before WCC', 'After WCC',
    #     'error', 'Suspicious',
    # ]

    data['distinct_table_cols'] = [
        'Package Name', 'Group', 'Before', 'After', 'Analysis Time',
        'error', 'Suspicious', 'State', 'VersionPair ID', 'Task ID'
    ]
    data['col_fields'] = list(map(
        lambda x: x.lower().replace(" ", "_"),
        data['distinct_table_cols']
    ))
    data['distinct_results'] = distinct_results.all()
    return render_template('report.html', **data)

@app.route('/label')
def label():
    session = Session()
    n = next_to_label(session)
    if n:
        return redirect(url_for('view_pair', id=n))
    else:
        return redirect('/report')

@app.route('/label_downloaded')
def label_downloaded():
    session = Session()
    return redirect(url_for('view_pair', id=next_to_label_downloaded(session)))

@app.route('/label_with/<string:pkg>')
def label_with(pkg=None):
    session = Session()
    return redirect(url_for('view_pair', id=next_to_label_with(session, pkg)))

@app.route('/versionpair/<int:id>/setlabel', methods=['POST'])
def set_label(id=None):
    session = Session()
    pair = session.query(VersionPair).filter_by(id=int(id)).one()
    pair.human_label = request.form['new_label']
    session.flush()
    session.commit()
    n = next_to_label(session)
    if n:
        return redirect(url_for('view_pair', id=n))
    else:
        return redirect('/report')

def random_unlabeled_pair_id(session):
    return session.query(VersionPairTaskModel).join(VersionPair).filter(VersionPair.human_label==None
        ).filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).filter(VersionPair.group == 'active_survey').order_by(
        func.random()).first().version_id

def next_to_label(session):
    n = session.query(VersionPairTaskModel).join(VersionPair).filter(VersionPair.human_label==None
        ).filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).filter(VersionPair.group.in_(['active_survey', 'retro_survey'])).order_by(
        VersionPairTaskModel.run_timestamp.desc()).first()

    if n:
        return n.version_id
    else:
        return None

def next_to_label_with(session, pkg):
    return session.query(VersionPairTaskModel).join(VersionPair).filter(VersionPair.human_label==None
        ).filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()
        ).filter(VersionPairTaskModel.json_result['system_extra_info']['new_rels'].as_string().like('%install_scripts%')
        ).filter(VersionPair.group == 'active_survey').order_by(
        VersionPairTaskModel.run_timestamp.desc()).first().version_id

def next_to_label_downloaded(session):
    return session.query(VersionPairTaskModel).join(VersionPair).\
        join(VersionPair.before).filter(Version.downloads > DL_THRESHOLD).\
        filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).\
        filter(VersionPair.human_label==None
        ).filter(VersionPairTaskModel.json_result['suspicious'].as_boolean()).order_by(
        VersionPairTaskModel.run_timestamp.desc()).first().version_id
