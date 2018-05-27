let kafka = require("kafka-node");
let child_process = require("child_process");
let fs = require("fs");

const client = new kafka.Client("localhost:2181");

const topics = [
    {
        topic: "img.crop.face"
    }
];

const options = {
    autoCommit: true,
    fetctMaxWaitMs: 1000,
    fectMaxBytes: 1024 * 1024,
    encoding: "buffer"
};

const consumer = new kafka.HighLevelConsumer(client, topics, options);

consumer.on("message", (message) => {

    let buf = new Buffer(message.value, "binary");
    let decodedMessage = JSON.parse(buf.toString());

    // check get data
    console.log(String(decodedMessage.name));
    let jsonFileName = decodedMessage.name.concat(".json");

    // wrtie json data
    fs.writeFile(jsonFileName, buf.toString(), (error) => {
        if (error) {
            return console.log(error);
        }

        // execute python script
        let python_script_cmd = "python ImageDisplay.py ".concat(jsonFileName);
        console.log(python_script_cmd);

        child_process.exec(python_script_cmd, (error, stdout, stderr) => {
            if (error) {
                return console.log("error executing script\n".concat(error));
            }

            if (stderr) {
                return console.log("error executing script\n".concat(stderr));
            }

            let result_str = stdout.concat("script executed");
            return console.log(result_str);
        });
    });
    
});

consumer.on("error", (error) => {
    console.log("error", err);
});

process.on("SIGINT", () => {
    consumer.close(true, () => {
        process.exit();
    })
});