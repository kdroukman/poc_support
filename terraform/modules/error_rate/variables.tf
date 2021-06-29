variable "filter" {
  default = "filter('sf_environment', '*') and filter('sf_service', '*') and filter('sf_operation','*')"
  description = "Which services, environments, etc to filter this service on. Allows all data by default"
}

variable "group_by" {
  default = "['sf_environment','sf_service','sf_operation']"
  description = "How to split the metric time series being reported on"

}

variable "current_window" {
  default="'5m'"
  description="The lookback window for this detector"

}

variable "histroic_window" {
  default="'1h'"
  description="The historic window to compare the current lookback window against"

}

variable "fire_growth_percent" {
  default="0.5"
  description="Percentage expressed in decimal, at what error growth rate to fire the alert"
}

variable "clear_growth_percent"{
  default="0.1"
  description="Percentage expressed in decimal, at what error growth rate to clear the alert"

}

variable "min_requests" {
  default="10"
  description="Volume of requests required before activating the alert"

}

variable "message_body" {
  type = string

  default = <<-EOF
    {{#if anomalous}}
	    Rule "{{{ruleName}}}" in detector "{{{detectorName}}}" triggered at {{timestamp}}.
    {{else}}
	    Rule "{{{ruleName}}}" in detector "{{{detectorName}}}" cleared at {{timestamp}}.
    {{/if}}

    {{#if anomalous}}
      Triggering condition: {{{readableRule}}}
    {{/if}}

    {{#if anomalous}}
      Signal value: {{inputs.A.value}}
    {{else}}
      Current signal value: {{inputs.A.value}}
    {{/if}}

    {{#notEmpty dimensions}}
      Signal details: {{{dimensions}}}
    {{/notEmpty}}

    {{#if anomalous}}
      {{#if runbookUrl}}
        Runbook: {{{runbookUrl}}}
      {{/if}}
      {{#if tip}}
        Tip: {{{tip}}}
      {{/if}}
    {{/if}}
  EOF
}

variable "sfx_prefix" {
  type        = string
  description = "Detector Prefix"
}