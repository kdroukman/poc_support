provider "signalfx" {
  auth_token = var.access_token
  api_url    = "https://api.${var.realm}.signalfx.com"
}

module "error_rate" {
  source     = "./modules/error_rate"
  sfx_prefix = var.sfx_prefix
}

resource "signalfx_detector" "z_test_detector" {
  name         = "zTest Detector"
  description  = "Alerts when the p90 latency in the last 5 minutes is higher than normal"
  program_text = <<-EOF
    from signalfx.detectors.apm.latency.historical_anomaly_v2 import historical_anomaly
    I = data('spans.duration.ns.p99', filter=filter('sf_kind', 'SERVER', 'CONSUMER') and filter('sf_service', '*') and filter('sf_operation', '*') and filter('sf_environment', '*') and (not filter('sf_dimensionalized', '*'))).promote('team').max(by=['sf_service', 'sf_operation']).publish(label='I')
    J = data('spans.duration.ns.p90', filter=filter('sf_kind', 'SERVER', 'CONSUMER') and filter('sf_service', '*') and filter('sf_operation', '*') and filter('sf_environment', '*') and (not filter('sf_dimensionalized', '*'))).promote('team').max(by=['sf_service', 'sf_operation']).publish(label='J')
    K = data('spans.duration.ns.median', filter=filter('sf_kind', 'SERVER', 'CONSUMER') and filter('sf_service', '*') and filter('sf_operation', '*') and filter('sf_environment', '*') and (not filter('sf_dimensionalized', '*'))).promote('team').max(by=['sf_service', 'sf_operation']).publish(label='K')
    historical_anomaly.deviations_from_norm(filter_=((filter('sf_service', '*') and filter('sf_operation', '*'))) and (filter('sf_kind', 'SERVER','CONSUMER')) and (filter('sf_environment', '*')), custom_filter=None, current_window='5m', historical_window='1h', cycle_length='1w', num_cycles=4, fire_num_dev_threshold=5, clear_num_dev_threshold=4, exclude_errors=True, volume_static_threshold=10, volume_relative_threshold=0.2, auto_resolve_after='30m').publish('zTest Detector')
  EOF
  rule {
    detect_label       = "zTest Detector"
    severity           = "Critical"
  }
}