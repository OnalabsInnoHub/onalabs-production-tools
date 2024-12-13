# ⚡️ Onalabs Inno-Hub BioT Upload Tool

The goal of the following Python script is to upload Onalab's devices to BioT and add them to an existing organization with a registration code to identify them. The steps to do so are:

1. Check if the BioT organization exists.
2. Upload the registration code.
3. Upload the device into an organization and assign a registration code to it. 

## 🚚 Integration with Logistic Excel
This script will be mainly used as an integration to the Logistic excel. In this case, only devices which follow the following conditions should be sent for upload:
1. "BioT" column is empty.
2. "BioT organization" column has an organization assigned.
Moreover once the script has finished the result should be added to the column "BioT" of the corresponding device.

## ⌨️ Script Arguments

The script requires at least 9 arguments.

| Parameter        | Short Form | Description                                                                                                                                          | Required | Data Type |
| ---------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | --------- |
| Environment      | -env       | Environment in BioT. Selectable values: "production" (for Production), "development" (for Development).                                              | True     | String    |
| Username         | -user      | Username to log into BioT for the corresponding environment.                                                                                              | True     | String    |
| Password         | -password  | Password to log into BioT for the corresponding environment.                                                                                              | True     | String    |
| SerialNumber     | -sn        | Serial Number of the device on which the tool operates.                                                                                             | True     | String    |
| Organization     | -org       | Organization to which the device will be assigned.                                                                                                 | True     | String    |
| RegistrationCode | -rc        | Registration Code to which the device will be assigned.                                                                                            | True     | String    |
| Description      | -description        | Advertising name of the device that will appear as a description in BioT.                                                                          | True     | String    |
| Version          | -version   | Version of the ONASPORT device.                                                                                                                    | True     | String    |
| OutputDirectory  | -output    | Directory where the traceability file is stored after completion.                                                                                                                            | True     | String    |

### Example

```shell
python BioTupload.py \
  -env "production" \
  -user "c.arechaga@onalabs.com" \
  -password "Carmen123." \
  -sn "1234567891" \
  -org "Tri-excellence.com" \
  -rc "2099BFF6-6648-4AAE-B43F-D9907A0731120" \
  -description "ONAS0000" \
  -version "2.0.0" \
  -output "C:\Users\Usuari\OS\PROD\shipping"
```

## 📝Traceability File

### Terminology

The name of the Traceability File must contain the serial number and the current timestamp, in the following format: `1XXXXXXXXXXXX_YYMMDD.json>`.

- `1XXXXXXXXXXXX`: Serial Number of the device.
- `YYMMDD`: Date in which the script has been executed.

### File Information
The traceability file must contain the result of the operation, including the serial number and the outcome of the upload. Use '0' if the device was uploaded correctly, or an error code indicating the reason for failure.

```json
{
  "serialNumber": "1234567891",
  "outputExecutionResult": 0,
}
```

## 💾 Final Output

The final output of this tool's execution will be a new file in the specified folder (through the Output Directory argument).
The console will print the path to the file, e.g., C:\Users\Usuari\OS\PROD\shipping\1234567892_241213.json

## ⚠️ Errors
Given the fact that the Onavital Flashing Tool includes user input, it is possible that errors occur. These will be reflected accordingly in the Traceability File. Below is a table that documents and summarizes the error codes:

| Error Code| Error Description                                                                         | 
| ----------| ----------------------------------------------------------------------------------------  | 
| 1         | Unable to format the filename correctly.                                                  | 
| 2         | Error encountered while logging content into a JSON file.                                 | 
| 3         | Issue encountered while managing data for JSON file dump.                                 |
| 4         | Difficulty in generating JSON content.                                                    |
| 5         | Error to check if serial number has the correct format.                                   |
| 6         | Error encountered during argument parsing.                                                |
| 7         | Difficulty in transforming the parsed object into a dictionary.                           |
| 8         | Error when interaction by GET method with API.                                            | 
| 9         | Error when interaction by POST method with API.                                           |
| 10        | Difficulty in creating URLs that interact with the APIs.                                  |
| 11        | Difficulty in log in.                                                                     |
| 12        | Error to get a list of the organizations available.                                       | 
| 13        | Error to retrieve the templates related to registration codes.                            | 
| 14        | Error to retrieve the templates related to ONASPORT devices.                              | 
| 15        | Difficulty in posting a registration code and/or a device.                                | 
| 16         | Error encountered while executing the main logic flow.                                   | 

