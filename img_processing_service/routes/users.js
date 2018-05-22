var express = require('express');
var router = express.Router();

let child_process = require('child_process');

/* GET users listing. */
router.get('/', function (req, res, next) {

    child_process.exec('python ')
    
    res.send('respond with a resource');
});

module.exports = router;
