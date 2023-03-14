const { TimestreamWrite } = require("@aws-sdk/client-timestream-write");
const writeClient = new TimestreamWrite();

exports.handler = async (event) => {
    try {
        if (event?.queryStringParameters?.auth !== process.env.AUTH_KEY) {
            return {
                statusCode: 401,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    error: 401,
                    message: "wrong auth query string"
                }),
            };
        }
        
        
        const currentTime = Date.now().toString();
    
        const dimensions = [
            {'Name': 'project', 'Value': 'opensour'}
        ];
    
        const records = Object.entries(event?.queryStringParameters)
            .filter(([key]) => key !== "auth")
            .map(
                ([key, value]) => ({
                    'Dimensions': dimensions,
                    'MeasureName': key,
                    'MeasureValue': String(value),
                    'MeasureValueType': 'DOUBLE',
                    'Time': currentTime.toString()
                })
            );
    
        if (records.length > 0) {
            const params = {
                DatabaseName: process.env.DATABASE_NAME,
                TableName: process.env.TABLE_NAME,
                Records: records
            };
          
            await writeClient.writeRecords(params);
        }
    
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                statusCode: 200,
                message: "success"
            }),
        };
    } catch (e) {
        console.error(e, e.message, e.stack);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                error: 500,
                message: e.message
            }),
        };
    }
};
