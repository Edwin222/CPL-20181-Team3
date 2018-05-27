
let kafka = require("kafka-node");

const client = new kafka.Client("localhost:2181", "face-cropper", {
    sessionTimeout: 300,
    spinDelay: 100,
    retries: 2
});

const producer = new kafka.HighLevelProducer(client);
producer.on("ready", () => {
    console.log("Face Cropper producer : Connected and Ready");
});

producer.on("error", (error) => {
    console.error(error);
});

const KafkaService = {
    sendRecord: ({ imgName, imgNumber, encodedRecord }, callback = () => { }) => {

        if (!imgName) {
            return callback(new Error('cannot read file name'));
        }

        const imgData = {
            name: imgName,
            number: imgNumber,
            timestamp: Date.now(),
            imgData_base64: encodedRecord
        };

        const jsonBuffer = new Buffer.from(JSON.stringify(imgData));
        const record = [
            {
                topic: "img.crop.face",
                messages: jsonBuffer,
                attributes: 1
            }
        ];

        producer.send(record, callback);
    }
};

module.exports = KafkaService;