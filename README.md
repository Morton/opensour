# Opensour

Opensour is an open-source IoT project for monitoring the growth of sourdough.

The Opensour device is an Raspberry Pico connected to an ultra-sonic distance sensor and a temperature/humidity sensor. The device periodically sends sensor data to an AWS TimeStream database.

## Building the device

`TODO: List of parts and instruction (with pictures and schematics) on how to assemble those.`

## Configuring AWS

You will need an AWS account to run the database. Login in to you AWS account, go to region Frankfurt (eu-central-1) and go to CloudFormation:
- Select "Create stack" / "With new resources (standard)"
- Select "Template is ready", "Upload a template file" and "Choose file", select the `cloud/stack.yaml` file from this repository, click "Next" and 
- Enter `opensour` as "Stack name", click "Next"
- You don't need to modify the next screen "Configure stack options", just click "Next again"
- On the final screen check the "I acknowledge that AWS CloudFormation might create IAM resources with custom names." box on the bottom and click "Submit"
- It will take some minutes but then the stack will show the status `CREATION_COMPLETE`
- Go to the "Outputs" tabs and copy the URL for `HostString`

## Connecting the device

Initially the device will not have any wifi credentials. You will need to set those up. 

Whenever the device cannot connect to wifi, it will open it's own wifi network:
- Connect to the ssid `opensour_****`, no password is required
- In your browser, open `192.168.4.1`
- Enter your local wifi name and password in the wifi setup ("Wifi configuration")
- Enter the Host string copied from AWS CloudFormation under "AWS configuration"
- Press the "Update" button
- The device should restart and connect to your wifi now

If everything works fine the small led should flash a couple of times and the stay on permanently, the device is now running. Every minute the big LED should light up green for some time, that's when the device takes measurements and transmits those to AWS.

## See the collected data

Currently this project doesn't contain any UI yet. For now, please use the [AWS Timestream Simple Visualizer](https://github.com/aws-samples/amazon-timestream-simple-visualizer) by running:

```sh
git clone https://github.com/aws-samples/amazon-timestream-simple-visualizer.git
cd amazon-timestream-simple-visualizer
yarn install # install dependencies
yarn start # run the application in debug
```

You will need an AWS Access key to connect it to Timestream, follow these instructions: [Managing access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) and configure those in the (Visualizer settings](http://localhost:3000/settings), also choose `eu-central-1` as Region. Now you should be able to add a new database connection to `opensour-metrics` with table `dough-metrics`

## Known bugs

1. Sometimes when restarting, the device cannot connect to the wifi network, even with correct credentials. Unplug the device for 5 minutes and then try again.
2. If the big green LED hasn't turned on for more then 2 minutes, the device has most-likely crashed. Unplug the device for 5 minutes and then try again.
3. If there is some sensor data missing the soldering points of the device may be weak and need to be renewed.

## Trouble shooting, meaning of the LEDs
The device has two LEDs, a green one on-board and a bigger green/red one soldered to the board. The LEDs have following states:

- *small LED* this one indicates the wifi status
  - *solid green* wifi is working properly and the device is connected to AWS
  - *blinking green* the device is connecting to the configured wifi network
  - *off* the device wasn't able to connect to wifi or AWS:
    - if there is a wifi network `opensour_****`, wifi isn't working. Connect to the network, open `192.168.4.1` and re-enter wifi credentials
    - if wifi worked but the connection to AWS doesn't, go to `http://opensour/` in your wifi and update the "host string" under "AWS configuration"

- *big LED* this indicates teh status once wifi is working
  - *green* the device is currently taking measures and transmitting those to AWS
  - *red* something went wrong
    - if this happens right after the led was green, something was wrong with transmitting measures
    - if this happens right from the start of the device, check the wifi setting
  - *off* the device is in idle status until next measurement
