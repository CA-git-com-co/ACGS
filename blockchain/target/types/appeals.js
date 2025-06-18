"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IDL = void 0;
exports.IDL = {
    "version": "0.1.0",
    "name": "appeals",
    "instructions": [
        {
            "name": "submitAppeal",
            "docs": [
                "Submit an appeal for a policy violation"
            ],
            "accounts": [
                {
                    "name": "appeal",
                    "isMut": true,
                    "isSigner": false
                },
                {
                    "name": "appellant",
                    "isMut": true,
                    "isSigner": true
                },
                {
                    "name": "systemProgram",
                    "isMut": false,
                    "isSigner": false
                }
            ],
            "args": [
                {
                    "name": "policyId",
                    "type": "u64"
                },
                {
                    "name": "violationDetails",
                    "type": "string"
                },
                {
                    "name": "evidenceHash",
                    "type": {
                        "array": [
                            "u8",
                            32
                        ]
                    }
                },
                {
                    "name": "appealType",
                    "type": {
                        "defined": "AppealType"
                    }
                }
            ]
        },
        {
            "name": "reviewAppeal",
            "docs": [
                "Review an appeal (first-tier automated/AI review)"
            ],
            "accounts": [
                {
                    "name": "appeal",
                    "isMut": true,
                    "isSigner": false
                },
                {
                    "name": "reviewer",
                    "isMut": false,
                    "isSigner": true
                }
            ],
            "args": [
                {
                    "name": "reviewerDecision",
                    "type": {
                        "defined": "ReviewDecision"
                    }
                },
                {
                    "name": "reviewEvidence",
                    "type": "string"
                },
                {
                    "name": "confidenceScore",
                    "type": "u8"
                }
            ]
        },
        {
            "name": "escalateToHumanCommittee",
            "docs": [
                "Escalate appeal to human committee"
            ],
            "accounts": [
                {
                    "name": "appeal",
                    "isMut": true,
                    "isSigner": false
                },
                {
                    "name": "escalator",
                    "isMut": false,
                    "isSigner": true
                }
            ],
            "args": [
                {
                    "name": "escalationReason",
                    "type": "string"
                },
                {
                    "name": "committeeType",
                    "type": {
                        "defined": "CommitteeType"
                    }
                }
            ]
        },
        {
            "name": "resolveWithRuling",
            "docs": [
                "Resolve appeal with final ruling"
            ],
            "accounts": [
                {
                    "name": "appeal",
                    "isMut": true,
                    "isSigner": false
                },
                {
                    "name": "resolver",
                    "isMut": false,
                    "isSigner": true
                }
            ],
            "args": [
                {
                    "name": "finalDecision",
                    "type": {
                        "defined": "FinalDecision"
                    }
                },
                {
                    "name": "rulingDetails",
                    "type": "string"
                },
                {
                    "name": "enforcementAction",
                    "type": {
                        "defined": "EnforcementAction"
                    }
                }
            ]
        },
        {
            "name": "getAppealStats",
            "docs": [
                "Get appeal statistics for governance reporting"
            ],
            "accounts": [
                {
                    "name": "appealStats",
                    "isMut": false,
                    "isSigner": false
                }
            ],
            "args": []
        }
    ],
    "accounts": [
        {
            "name": "appeal",
            "docs": [
                "Appeal Account: Represents a single appeal case"
            ],
            "type": {
                "kind": "struct",
                "fields": [
                    {
                        "name": "id",
                        "docs": [
                            "Unique appeal identifier"
                        ],
                        "type": "u64"
                    },
                    {
                        "name": "policyId",
                        "docs": [
                            "Policy ID being appealed"
                        ],
                        "type": "u64"
                    },
                    {
                        "name": "appellant",
                        "docs": [
                            "Public key of the appellant"
                        ],
                        "type": "publicKey"
                    },
                    {
                        "name": "violationDetails",
                        "docs": [
                            "Detailed description of the violation"
                        ],
                        "type": "string"
                    },
                    {
                        "name": "evidenceHash",
                        "docs": [
                            "Hash of supporting evidence (stored off-chain)"
                        ],
                        "type": {
                            "array": [
                                "u8",
                                32
                            ]
                        }
                    },
                    {
                        "name": "appealType",
                        "docs": [
                            "Type of appeal"
                        ],
                        "type": {
                            "defined": "AppealType"
                        }
                    },
                    {
                        "name": "status",
                        "docs": [
                            "Current status of the appeal"
                        ],
                        "type": {
                            "defined": "AppealStatus"
                        }
                    },
                    {
                        "name": "submittedAt",
                        "docs": [
                            "When the appeal was submitted"
                        ],
                        "type": "i64"
                    },
                    {
                        "name": "reviewDeadline",
                        "docs": [
                            "Deadline for initial review"
                        ],
                        "type": "i64"
                    },
                    {
                        "name": "reviewer",
                        "docs": [
                            "Who reviewed the appeal (if any)"
                        ],
                        "type": {
                            "option": "publicKey"
                        }
                    },
                    {
                        "name": "reviewDecision",
                        "docs": [
                            "Review decision (if any)"
                        ],
                        "type": {
                            "option": {
                                "defined": "ReviewDecision"
                            }
                        }
                    },
                    {
                        "name": "reviewEvidence",
                        "docs": [
                            "Evidence provided by reviewer"
                        ],
                        "type": "string"
                    },
                    {
                        "name": "confidenceScore",
                        "docs": [
                            "Confidence score of the review (0-100)"
                        ],
                        "type": "u8"
                    },
                    {
                        "name": "reviewedAt",
                        "docs": [
                            "When the appeal was reviewed"
                        ],
                        "type": {
                            "option": "i64"
                        }
                    },
                    {
                        "name": "escalationReason",
                        "docs": [
                            "Reason for escalation (if escalated)"
                        ],
                        "type": {
                            "option": "string"
                        }
                    },
                    {
                        "name": "committeeType",
                        "docs": [
                            "Type of committee handling escalation"
                        ],
                        "type": {
                            "option": {
                                "defined": "CommitteeType"
                            }
                        }
                    },
                    {
                        "name": "escalatedAt",
                        "docs": [
                            "When escalated to human review"
                        ],
                        "type": {
                            "option": "i64"
                        }
                    },
                    {
                        "name": "escalationCount",
                        "docs": [
                            "Number of times escalated"
                        ],
                        "type": "u8"
                    },
                    {
                        "name": "humanReviewDeadline",
                        "docs": [
                            "Deadline for human review"
                        ],
                        "type": {
                            "option": "i64"
                        }
                    },
                    {
                        "name": "finalDecision",
                        "docs": [
                            "Final decision (if resolved)"
                        ],
                        "type": {
                            "option": {
                                "defined": "FinalDecision"
                            }
                        }
                    },
                    {
                        "name": "rulingDetails",
                        "docs": [
                            "Detailed ruling explanation"
                        ],
                        "type": "string"
                    },
                    {
                        "name": "enforcementAction",
                        "docs": [
                            "Enforcement action to be taken"
                        ],
                        "type": {
                            "option": {
                                "defined": "EnforcementAction"
                            }
                        }
                    },
                    {
                        "name": "resolvedAt",
                        "docs": [
                            "When the appeal was resolved"
                        ],
                        "type": {
                            "option": "i64"
                        }
                    },
                    {
                        "name": "resolver",
                        "docs": [
                            "Who resolved the appeal"
                        ],
                        "type": {
                            "option": "publicKey"
                        }
                    }
                ]
            }
        },
        {
            "name": "appealStats",
            "docs": [
                "Appeal Statistics Account"
            ],
            "type": {
                "kind": "struct",
                "fields": [
                    {
                        "name": "totalAppeals",
                        "type": "u64"
                    },
                    {
                        "name": "approvedAppeals",
                        "type": "u64"
                    },
                    {
                        "name": "rejectedAppeals",
                        "type": "u64"
                    },
                    {
                        "name": "pendingAppeals",
                        "type": "u64"
                    },
                    {
                        "name": "averageResolutionTime",
                        "type": "u64"
                    },
                    {
                        "name": "humanEscalationRate",
                        "type": "u8"
                    }
                ]
            }
        }
    ],
    "types": [
        {
            "name": "AppealType",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "PolicyViolation"
                    },
                    {
                        "name": "ProcessError"
                    },
                    {
                        "name": "NewEvidence"
                    },
                    {
                        "name": "ConstitutionalChallenge"
                    }
                ]
            }
        },
        {
            "name": "AppealStatus",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "Submitted"
                    },
                    {
                        "name": "UnderReview"
                    },
                    {
                        "name": "PendingHumanReview"
                    },
                    {
                        "name": "EscalatedToHuman"
                    },
                    {
                        "name": "Approved"
                    },
                    {
                        "name": "Rejected"
                    },
                    {
                        "name": "ModifiedApproval"
                    },
                    {
                        "name": "Expired"
                    }
                ]
            }
        },
        {
            "name": "ReviewDecision",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "Approve"
                    },
                    {
                        "name": "Reject"
                    },
                    {
                        "name": "Escalate"
                    }
                ]
            }
        },
        {
            "name": "CommitteeType",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "Technical"
                    },
                    {
                        "name": "Governance"
                    },
                    {
                        "name": "Ethics"
                    },
                    {
                        "name": "Constitutional"
                    }
                ]
            }
        },
        {
            "name": "FinalDecision",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "Uphold"
                    },
                    {
                        "name": "Overturn"
                    },
                    {
                        "name": "Modify"
                    }
                ]
            }
        },
        {
            "name": "EnforcementAction",
            "type": {
                "kind": "enum",
                "variants": [
                    {
                        "name": "None"
                    },
                    {
                        "name": "PolicyUpdate"
                    },
                    {
                        "name": "SystemAlert"
                    },
                    {
                        "name": "TemporaryExemption"
                    }
                ]
            }
        }
    ],
    "events": [
        {
            "name": "AppealSubmittedEvent",
            "fields": [
                {
                    "name": "appealId",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "policyId",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "appellant",
                    "type": "publicKey",
                    "index": false
                },
                {
                    "name": "appealType",
                    "type": {
                        "defined": "AppealType"
                    },
                    "index": false
                },
                {
                    "name": "submittedAt",
                    "type": "i64",
                    "index": false
                }
            ]
        },
        {
            "name": "AppealReviewedEvent",
            "fields": [
                {
                    "name": "appealId",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "reviewer",
                    "type": "publicKey",
                    "index": false
                },
                {
                    "name": "decision",
                    "type": {
                        "defined": "ReviewDecision"
                    },
                    "index": false
                },
                {
                    "name": "confidenceScore",
                    "type": "u8",
                    "index": false
                },
                {
                    "name": "reviewedAt",
                    "type": "i64",
                    "index": false
                }
            ]
        },
        {
            "name": "AppealEscalatedEvent",
            "fields": [
                {
                    "name": "appealId",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "committeeType",
                    "type": {
                        "defined": "CommitteeType"
                    },
                    "index": false
                },
                {
                    "name": "escalationCount",
                    "type": "u8",
                    "index": false
                },
                {
                    "name": "escalatedAt",
                    "type": "i64",
                    "index": false
                }
            ]
        },
        {
            "name": "AppealResolvedEvent",
            "fields": [
                {
                    "name": "appealId",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "finalDecision",
                    "type": {
                        "defined": "FinalDecision"
                    },
                    "index": false
                },
                {
                    "name": "enforcementAction",
                    "type": {
                        "defined": "EnforcementAction"
                    },
                    "index": false
                },
                {
                    "name": "resolver",
                    "type": "publicKey",
                    "index": false
                },
                {
                    "name": "resolvedAt",
                    "type": "i64",
                    "index": false
                }
            ]
        },
        {
            "name": "AppealStatsEvent",
            "fields": [
                {
                    "name": "totalAppeals",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "approvedAppeals",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "rejectedAppeals",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "pendingAppeals",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "averageResolutionTime",
                    "type": "u64",
                    "index": false
                },
                {
                    "name": "humanEscalationRate",
                    "type": "u8",
                    "index": false
                }
            ]
        }
    ],
    "errors": [
        {
            "code": 6000,
            "name": "ViolationDetailsTooLong",
            "msg": "Violation details are too long."
        },
        {
            "code": 6001,
            "name": "ReviewEvidenceTooLong",
            "msg": "Review evidence is too long."
        },
        {
            "code": 6002,
            "name": "EscalationReasonTooLong",
            "msg": "Escalation reason is too long."
        },
        {
            "code": 6003,
            "name": "RulingDetailsTooLong",
            "msg": "Ruling details are too long."
        },
        {
            "code": 6004,
            "name": "InvalidConfidenceScore",
            "msg": "Invalid confidence score. Must be 0-100."
        },
        {
            "code": 6005,
            "name": "InvalidAppealStatus",
            "msg": "Appeal is not in the correct status for this operation."
        },
        {
            "code": 6006,
            "name": "ReviewDeadlineExpired",
            "msg": "Review deadline has expired."
        },
        {
            "code": 6007,
            "name": "CannotEscalate",
            "msg": "Appeal cannot be escalated in its current status."
        },
        {
            "code": 6008,
            "name": "MaxEscalationsReached",
            "msg": "Maximum number of escalations reached."
        },
        {
            "code": 6009,
            "name": "CannotResolve",
            "msg": "Appeal cannot be resolved in its current status."
        }
    ]
};
