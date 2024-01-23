The purpose of the RogueOne is to track
when a piece of data originating in one package becomes available to another package.

Consider a small JS program, where data from a remote API is saved to disk:
```javascript
const fs = require('fs')
const api = require('api') // NPM package wrapping a web request
fs.writeFileSync('file.txt', api.getData())
```

It is our goal to capture that data has flowed from the remote api to the filesystem.
In this case, the `fs.writeFileSync` function is a property of the `fs` module, and the object which is sent
to that function is a return value of `api.getData`, which is itself a property of `api`.  If importing a module using
`require` creates a tag on the resulting object, we want to show that in some way, the tag `api` reaches the tag `fs`.
From this simple example, we can see that this 'reaching' relationship must include at least:
- Property references, such as `fs.writeFileSync` and `api.getData`
- Function return values such as `api.getData()`
- Function parameter passing, such as when the result of `api.getData()` is passed to `fs.writeFileSync`.

Now, consider another example, where an imported module is configured with a secret key:
```javascript
const api = require('api');
api.options.key = process.env['SECRET_KEY'];
api.remoteOperation();
```

Clearly, the secret key was taken from the environment and passed to the api object, or else the remote operation
could not succeed.  Therefore, just mutating an object received from a remote library is enough to pass information
to that library.  No function call is required.  Now, consider another example:

```javascript
const api = require('api');
const util = require('util')
api.options.key = process.env['SECRET_KEY']
api.options.other = util.info
```

Here, the `api` library receives data from two sources, the process environment and the `util` library.  This creates
a transitive link between `util` and the process environment, since inside `api`, the secret key may be in turn inserted
into `util.info`.  However, capturing this transitive data-flow gives us less information than keeping the two immediate
data-flows.  A star-like structure of data-flows would collapse into a dense web if all transitive flows were present.

These examples create several constraints, which motivate our strategy for finding data-flows.  
- Traversing from one tag to another may require going both from an object to its properties and from the property
to the parent object.
- Traversing from one tag to another may require going from a return value to the function which created it.
- Traversing from one tag to another may require crossing from the parameters of a function call to the return
value from that function call.
- Making all these connections bidirectional, and capturing all the tags reachable from one tag will result
in a collapsed data-flow structure.

In order to overcome these challenges, RogueOne introduces a graph structure called the 
Object Data-Flow Relationship Graph (ODRG). 
The ODRG tracks three types of data relationships: `CALL_EFFECT`, `PROP_REF`, and `CONTRIBUTES_TO`.
Using these three relationships and a two-phase traversal process, we find the data-flows of the target program.

Consider the most basic JS program:
```javascript
var x = {};
```
Here, the object stored in the variable `x` will be represented as a node in the ODRG.  As a base JS object,
`x` starts with a `PROP_REF` edge leading to `Object.prototype`.  This edge is labeled with the name `__proto__`,
and represents the default prototype all objects start with.

Suppose we assign `x` to another variable as well:
```javascript
var y = x;
```
Since reassignment / aliasing does not create another object, this has no effect on the ODRG.  However, assignment to 
a property creates new relationships:

```javascript
x.name = "Alice"
```
This creates a new node representing the string `"Alice"` and links `x` to that node via a `PROP_REF` edge `name`.  

Now we examine a simple data flow:
```javascript
var a = 2;
var b = 4;
var sum = a + b;
```

Here, `a` and `b` are operands of an operation resulting in `sum`.  Therefore, there is a `CONTRIBUTES_TO` edge
leading from each of them to `sum`.  This indicates that `a` and `b` were used to create `sum`, but `sum` does not
hold a reference to them.  Parameters of functions are treated similarly:
```javascript
var fs = require('fs');
var path = 'dataFile.txt';
var data = fs.readFileSync(path);
```

Here, the `path` object is passed as a parameter to `fs.readFileSync`.  The call to `fs.readFileSync` creates a new
object, `data`, and `path` is linked to `data` by a `CONTRIBUTES_TO` edge.  In addition, since `data` is the result
of a call to the `fs.readFileSync` object, there is a `CALL_EFFECT` edge leading from `fs.readFileSync` to `data`.

This interaction is an example of passing internal data to an external API, exactly the type of interaction that
RogueOne is interested in capturing.  Specifically, we want to capture that a piece of local data was passed to `fs`.
RogueOne accomplishes this by finding a node in the graph where the data flow from `path` becomes referenceable by `fs`.

By following `PROP_REF` edges from `fs`, we can reach the `readFileSync` object, then follow the `CALL_EFFECT` edge
to the `data` object.  This combination of `PROP_REF` and `CALL_EFFECT` establishes referenceability, and we annotate
the `data` node accordingly.  
Then, we follow the `CONTRIBUTES_TO` edge from `path` to `data`, and note that the data flow from `path` to `fs` exists.

Now, consider a more complex example.  Axios is a commonly used JavaScript API client.  Normal use might look like the
following snippet:
```javascript
const axios = require('axios');
const fs = require('fs');
const instance = axios.create({
  baseURL: 'https://example.com/api/',
});
instance.get('/scripts?ID=12345')
  .then(function (response) {
    fs.writeFileSync('attack.sh', response.data)
    console.log(response);
  })
  .catch(function (error) {
    // handle error
    console.log(error);
  })
```

Here, we want to capture that data is received from the internet, then passed to the `fs.writeFileSync` function.
We must find a node where the data flow from `axios` is reachable by `fs`.  Here, we note another case that creates
an edge: when a callback `c` with parameter `p` is passed to a function `f`, `f -CONTRIBUTES_TO-> p`.
Also, even though no result is saved from `fs.writeFileSync`, an implicit result object is created and linked to
the function and parameters. First we will trace from `axios` to that result:

`require('axios') -PROP_REF-> create 
    -CALL_EFFECT-> instance 
    -PROP_REF-> get 
    -CONTRIBUTES_TO-> response 
    -PROP_REF-> data 
    -CONTRIBUTES_TO-> result`

Then, we will trace from `fs` to that result:
`require('fs') -PROP_REF-> writeFileSync 
    -CALL_EFFECT-> result`

Observe here that from `axios` to the result all three edges are present, but from `fs` to the result only `PROP_REF`
and `CALL_EFFECT` are present.  This motivates the two traversals performed by RogueOne:

- Phase 1, sink extension, which traverses from a library down through `PROP_REF` and `CALL_EFFECT` edges.
- Phase 2, source dispatching, which traverses from a library down through all three edge types.

Where these two traversals meet, a data flow is created.

Unfortunately, JS has a densely connected object graph.  Every object has a `PROP_REF` path to `Object.prototype`,
so these traversals would result in data flows from every origin to every destination.  Therefore, a whitelist
of built-in prototype objects must be incorporated.  The data-flow traversals do not cross `PROP_REF` edges through
these pre-existing objects, in order to prevent a trivial collapse of the data-flow network.

In the example above, RogueOne finds numerous data flows between local objects and objects originating with `axios`.
For instance, the options object which is passed to `axios.create` is also linked to the `get`, `then`, and `catch`
methods originating from `axios` by traversal through `CALL_EFFECT` and `PROP_REF` edges.  However, all these objects
are controlled by the same code: `axios`.  Ultimately, passing data to these objects requires trusting the same package
authors, the authors of `axios`.  RogueOne expresses this concept through a novel abstraction called a _trust domain_.
Every required library or builtin API is assigned a trust domain, and rather than tracking data-flows between objects,
Rogue One tracks data-flows across trust domains.  The traversals described above are used to spread these 
trust domains through the graph and find where they intersect:

- Phase 1: From each trust domain root, follow `PROP_REF` and `CALL_EFFECT` edges, 
not visiting whitelisted objects through `PROP_REF` edges,
and mark each reached node with origin trust domain.  Each marked node becomes a sink for that trust domain.
- Phase 2: From each trust domain root, follow all three edge types, not visiting whitelisted objects through 
`PROP_REF` edges.  When a visited node has been marked with a trust domain in Phase 1, it has reached a sink.  Then, 
record a data-flow from the current trust domain to the marked one.

Trust domains provide an intuitive basis for considering whether a data-flow may be malicious.
They correspond to the external APIs provided by Node.JS and the browser, or to packages on the NPM registry.
In addition, if a JS file cannot be analyzed, it can be conveniently regarded as an independent trust domain,
and data-flow into and out of that file can be similarly tracked.
We have empirically observed that typical updates do not create new cross-domain data-flows.  Instead,
they change what functions are called, or how information is processed.  Trust domains allow these superficial changes
in information flow to be disregarded, compacting the set of data-flows to readable package and API level connections.
The granularity of trust domain assignment can be configured for the `local` trust domain, with the default state that
all local data is in one trust domain, and a paranoid mode in which every independent value is a separate trust domain.

However, this process still gives a large set of data-flows. Since RogueOne is targeting rogue updates, it compares
the set of data flows across two versions of a package and finds the new ones.  These new data flows are
considered suspicious and should be investigated.


Other topics
- module.exports 
- ODRG extraction from odgen graph
- Additions to the odgen graph to allow ODRG construction