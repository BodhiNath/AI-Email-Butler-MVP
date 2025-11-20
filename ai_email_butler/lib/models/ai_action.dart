import 'dart:convert';

class AiActionSuggestion {
  final String action;
  final double confidence;
  final String sendPermission;
  final String? replyText;
  final String? suggestedWorkflowId;

  AiActionSuggestion({
    required this.action,
    required this.confidence,
    required this.sendPermission,
    this.replyText,
    this.suggestedWorkflowId,
  });

  factory AiActionSuggestion.fromJson(Map<String, dynamic> json) {
    return AiActionSuggestion(
      action: json['action'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      sendPermission: json['send_permission'] as String,
      replyText: json['reply_text'] as String?,
      suggestedWorkflowId: json['suggested_workflow_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'action': action,
      'confidence': confidence,
      'send_permission': sendPermission,
      'reply_text': replyText,
      'suggested_workflow_id': suggestedWorkflowId,
    };
  }
}

class EmailContext {
  final String subject;
  final String body;
  final String sender;
  final String? threadHistory;
  final String userId;
  final String workflowRules;

  EmailContext({
    required this.subject,
    required this.body,
    required this.sender,
    this.threadHistory,
    required this.userId,
    required this.workflowRules,
  });

  Map<String, dynamic> toJson() {
    return {
      'subject': subject,
      'body': body,
      'sender': sender,
      'thread_history': threadHistory,
      'user_id': userId,
      'workflow_rules': workflowRules,
    };
  }
}
