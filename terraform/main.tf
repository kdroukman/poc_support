provider "signalfx" {
  auth_token = var.access_token
  api_url    = "https://api.${var.realm}.signalfx.com"
}

module "error_rate" {
  source     = "./modules/error_rate"
  sfx_prefix = var.sfx_prefix
}
