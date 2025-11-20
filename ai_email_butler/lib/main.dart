import 'package:flutter/material.dart';
import 'models/ai_action.dart';
import 'services/api_service.dart';
import 'exceptions/api_exceptions.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Email Butler MVP',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const EmailDashboard(),
    );
  }
}

class EmailDashboard extends StatefulWidget {
  const EmailDashboard({super.key});

  @override
  State<EmailDashboard> createState() => _EmailDashboardState();
}

class _EmailDashboardState extends State<EmailDashboard> {
  late final ApiService _apiService;
  AiActionSuggestion? _suggestion;
  bool _isLoading = false;
  String _statusMessage = 'Ready to process email.';
  String? _errorMessage;

  // Mock Email Data for demonstration
  final EmailContext _mockEmail = EmailContext(
    subject: 'Follow up on the Q3 report',
    body: 'Hi, can you please send over the final Q3 report by end of day today? Thanks!',
    sender: 'boss@company.com',
    userId: 'mock_user_123',
    workflowRules: 'If sender is boss@company.com, draft a polite reply confirming receipt and asking for a 24-hour extension.',
  );

  @override
  void initState() {
    super.initState();
    // Initialize API service with mock JWT token
    // In a real app, this would come from an authentication provider
    _apiService = ApiService(
      jwtToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtb2NrX3VzZXJfMTIzIn0.test',
      userId: 'mock_user_123',
    );
  }

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }

  Future<void> _processEmail() async {
    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending email context to AI backend...';
      _suggestion = null;
      _errorMessage = null;
    });

    try {
      final suggestion = await _apiService.suggestAction(_mockEmail);
      setState(() {
        _suggestion = suggestion;
        _statusMessage = 'AI Suggestion Received!';
      });
    } on ValidationException catch (e) {
      _setError('Validation Error: ${e.message}');
    } on AuthenticationException catch (e) {
      _setError('Authentication Error: Please log in again.');
    } on RateLimitException catch (e) {
      _setError('Rate Limit: ${e.message}');
    } on NetworkException catch (e) {
      _setError('Network Error: ${e.message}');
    } on ServerException catch (e) {
      _setError('Server Error: ${e.message}');
    } on ApiException catch (e) {
      _setError('API Error: ${e.message}');
    } catch (e) {
      _setError('Unexpected Error: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _setError(String message) {
    setState(() {
      _statusMessage = 'Error occurred';
      _errorMessage = message;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Email Butler MVP'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _processEmail,
            tooltip: 'Process Mock Email',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            // Status indicator
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _errorMessage != null ? Colors.red.shade50 : Colors.green.shade50,
                border: Border.all(
                  color: _errorMessage != null ? Colors.red : Colors.green,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Status: $_statusMessage',
                    style: TextStyle(
                      color: _errorMessage != null ? Colors.red : Colors.green,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      _errorMessage!,
                      style: const TextStyle(
                        color: Colors.red,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),

            // Email preview
            const Text(
              'Mock Incoming Email:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ListTile(
              title: Text(_mockEmail.subject),
              subtitle: Text('From: ${_mockEmail.sender}'),
              trailing: const Icon(Icons.email),
              tileColor: Colors.blue.shade50,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Body: ${_mockEmail.body}',
                style: const TextStyle(fontSize: 14),
              ),
            ),
            const SizedBox(height: 24),

            // Action button
            Center(
              child: _isLoading
                  ? const SizedBox(
                      height: 40,
                      width: 40,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : ElevatedButton.icon(
                      onPressed: _processEmail,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Run AI Workflow'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                      ),
                    ),
            ),
            const SizedBox(height: 24),
            const Divider(height: 30),

            // Suggestion results
            if (_suggestion != null)
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Action Suggestion:',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildSuggestionCard(
                        'Action',
                        _suggestion!.action,
                        Colors.blue,
                      ),
                      _buildSuggestionCard(
                        'Confidence',
                        '${(_suggestion!.confidence * 100).toStringAsFixed(0)}%',
                        Colors.orange,
                      ),
                      _buildSuggestionCard(
                        'Send Permission',
                        _suggestion!.sendPermission,
                        Colors.purple,
                      ),
                      if (_suggestion!.replyText != null)
                        _buildSuggestionCard(
                          'Draft Reply',
                          _suggestion!.replyText!,
                          Colors.green,
                        ),
                      if (_suggestion!.suggestedWorkflowId != null)
                        _buildSuggestionCard(
                          'Workflow ID',
                          _suggestion!.suggestedWorkflowId!,
                          Colors.teal,
                        ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionCard(String title, String value, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$title:',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(fontSize: 14),
          ),
        ],
      ),
    );
  }
}
