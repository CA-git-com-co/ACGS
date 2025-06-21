# ACGS-1 IAM Module Outputs

output "eks_service_role_arn" {
  description = "ARN of the EKS service role"
  value       = aws_iam_role.eks_service_role.arn
}

output "eks_node_group_role_arn" {
  description = "ARN of the EKS node group role"
  value       = aws_iam_role.eks_node_group_role.arn
}

output "acgs_service_role_arn" {
  description = "ARN of the ACGS service role"
  value       = aws_iam_role.acgs_service_role.arn
}

output "constitutional_governance_role_arn" {
  description = "ARN of the constitutional governance role"
  value       = aws_iam_role.constitutional_governance_role.arn
}
