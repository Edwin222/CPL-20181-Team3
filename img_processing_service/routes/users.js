const path = require('path');
const fs = require('fs');
const producer = require('./kafka_producer');

var express = require('express');
var router = express.Router();

let child_process = require('child_process');

/* GET users listing. */
router.post('/', function (req, res, next) {

    let name = String(req.query.name);
    let path = String(req.query.path);
    let imgNum = String(req.query.num);

    let python_script_cmd = "python py-script\\img_convert.py ";

    path = path.replace(/\\/gi, "\\\\");

    python_script_cmd = python_script_cmd.concat(name)
        .concat(" ")
        .concat(imgNum)
        .concat(" ")
        .concat(path);

    let jsonFileName = name.concat(".json");
    
    console.log(python_script_cmd);
    console.log(jsonFileName);
    
    child_process.exec(python_script_cmd, (error, stdout, stderr) => {
        if (error) {
            console.log("error executing script\n".concat(error));
            res.send("error executing script\n".concat(error));
        }

        if (stderr) {
            console.log("error executing script\n".concat(stderr));
            res.send("error executing script\n".concat(stderr));
        }

        let result_str = stdout.concat("script executed");
        console.log(result_str);

        // read json file
        fs.readFile(jsonFileName, 'utf8', (err, data) => {
            if (!data) {
                console.log("can't find face in capture image");
                res.send(result_str);
            }
            else {
                executedResult = JSON.parse(data);

                // produce message by kafka
                producer.sendRecord({
                    imgName: executedResult.imgName,
                    imgNum: executedResult.imgNumber,
                    encodedRecord: executedResult.encodeRecord
                }, () => {
                    res.send(result_str);
                });
            }
        });
    });
});

module.exports = router;
