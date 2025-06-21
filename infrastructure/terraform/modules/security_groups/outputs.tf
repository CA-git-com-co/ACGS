# ACGS-1 Security Groups Module Outputs

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = aws_security_group.eks_cluster.id
}

output "eks_nodes_security_group_id" {
  description = "EKS nodes security group ID"
  value       = aws_security_group.eks_nodes.id
}

output "acgs_services_security_group_id" {
  description = "ACGS services security group ID"
  value       = aws_security_group.acgs_services.id
}
