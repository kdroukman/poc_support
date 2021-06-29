# Splunk POC Jumpstart
**Requires Terraform (minimum) v0.14**

## Clone this repository:

`git clone https://github.com/signalfx/signalfx-jumpstart.git`

## Initialise Terraform

```
$ terraform init --upgrade
```

## Create a workspace (Optional)

```
$ terraform workspace new my_workspace
```
Where `my_workspace` is the name of your workspace

## Review the execution plan

```
$ terraform plan -var="access_token=abc123" -var="realm=us1"
```

Where `access_token` is the Splunk Access Token and `realm` is either `eu0`, `us0`, `us1` or `us2`

## Apply the changes

```
$ terraform apply -var="access_token=abc123" -var="realm=us1"
```

## Destroy everything (if you must)

If you created a workspace you will first need to ensure you are in the correct workspace e.g.

```
$ terraform workspace select my_workspace
```
Where `my_workspace` is the name of your workspace

```
$ terraform destroy -var="access_token=abc123" -var="realm=us1"
```

# Deploying a module and programmatically changing detector settings

This package contains a number of modules for different detectors. 
Within each module you can additional set a number of variables specific to each detector.
This can be used to modify your detector settings. For example

```
terraform apply -var="access_token=abc123" -var="realm=us1" -target=module.error_rate -var="current_window='1m'" -var="historic_window='3h'" -var="fire_growth_percent=0.25" -var="min_requests=15"
```

The above will modify the sudden change alert for error rate growth to the respective settings.
See `./modules/error_rate/variables.tf` for default values and variables that can be set.

