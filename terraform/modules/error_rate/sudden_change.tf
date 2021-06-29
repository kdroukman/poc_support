resource "signalfx_detector" "error_sudden_change" {
  name         = "${var.sfx_prefix} error rate % greater than historical norm"
  description  = "Alerts when error rate for a service is significantly higher than normal, as compared to the historic window"
  program_text = <<-EOF
    from signalfx.detectors.apm.errors import streams
    from signalfx.detectors.apm.errors import conditions

    f = ${var.filter}
    grp = ${var.group_by}
    cw=${var.current_window}
    hw=${var.histroic_window}
    fgt=${var.fire_growth_percent}
    cgt=${var.clear_growth_percent}
    num_v=${var.min_requests}

    A = data('spans.count', filter=f and filter('sf_error', 'true'), rollup='delta').sum(by=['sf_environment','sf_service','sf_operation']).publish(label='A', enable=False)
    B = data('spans.count', filter=f, rollup='delta').sum(by=['sf_environment','sf_service','sf_operation']).publish(label='B', enable=False)
    C = combine(100*((A if A is not None else 0) / B)).publish(label='C')

    c = conditions.percentage_growth(current_window=cw, preceding_window=hw,fire_growth_threshold=fgt, clear_growth_threshold=cgt, filter_=f, group_by=grp)
    v = conditions.volume(duration_=cw, shift=duration(0), filter_=f, group_by=grp,num_attempt_threshold=num_v)

    detect(c['on'] and v, off=c['off']).publish('service error rate sudden change detector')
  EOF
  rule {
    detect_label       = "service error rate sudden change detector"
    severity           = "Warning"
    parameterized_body = var.message_body
  }
}