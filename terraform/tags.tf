locals {
  common_tags = merge(
    {
      ManagedBy = "Tofu"
      Project   = "thin-controller"
    },
    var.tags
  )
}
