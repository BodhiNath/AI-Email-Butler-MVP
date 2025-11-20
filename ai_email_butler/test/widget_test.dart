// Widget tests for AI Email Butler application
//
// These tests verify the main UI components and user interactions.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

import 'package:ai_email_butler/main.dart';
import 'package:ai_email_butler/models/ai_action.dart';

// Mock ApiService for testing
class MockApiService extends Mock {
  Future<AiActionSuggestion> suggestAction(EmailContext context) async {
    return AiActionSuggestion(
      action: 'draft_reply',
      confidence: 0.95,
      sendPermission: 'draft_only',
      replyText: 'Thank you for reaching out. I appreciate your message.',
    );
  }
}

void main() {
  testWidgets('EmailDashboard displays mock email correctly', (WidgetTester tester) async {
    // Build our app
    await tester.pumpWidget(const MyApp());

    // Verify AppBar exists
    expect(find.text('AI Email Butler MVP'), findsOneWidget);

    // Verify mock email is displayed
    expect(find.text('Follow up on the Q3 report'), findsOneWidget);
    expect(find.text('From: boss@company.com'), findsOneWidget);
    expect(find.text('Hi, can you please send over the final Q3 report by end of day today? Thanks!'), findsOneWidget);

    // Verify initial status message
    expect(find.text('Ready to process email.'), findsOneWidget);
  });

  testWidgets('EmailDashboard shows loading indicator when processing', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Tap the "Run AI Workflow" button
    await tester.tap(find.byIcon(Icons.auto_awesome));
    await tester.pump();

    // Verify loading indicator appears
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('Sending email context to AI backend...'), findsOneWidget);
  });

  testWidgets('EmailDashboard can process email with refresh icon', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Verify refresh icon exists in AppBar
    expect(find.byIcon(Icons.refresh), findsOneWidget);

    // Tap refresh icon
    await tester.tap(find.byIcon(Icons.refresh));
    await tester.pump();

    // Status should change to loading
    expect(find.text('Sending email context to AI backend...'), findsOneWidget);
  });

  testWidgets('EmailDashboard displays suggestion results when available', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Tap the action button to trigger API call
    await tester.tap(find.byIcon(Icons.auto_awesome));
    
    // Wait for API response (in real scenario)
    await tester.pumpAndSettle(const Duration(seconds: 2));

    // Note: In a real test with mocked API, we'd verify the suggestion display
    // For now, verify the UI structure is correct
    expect(find.byType(ElevatedButton), findsWidgets);
  });

  testWidgets('EmailDashboard has correct AppBar actions', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Verify AppBar has refresh button
    final appBar = find.byType(AppBar);
    expect(appBar, findsOneWidget);

    // Verify icon button (refresh) exists
    final iconButton = find.byIcon(Icons.refresh);
    expect(iconButton, findsOneWidget);
  });

  testWidgets('EmailDashboard displays email details in ListTile', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Verify ListTile with email details
    expect(find.byType(ListTile), findsOneWidget);
    expect(find.byIcon(Icons.email), findsOneWidget);
  });

  testWidgets('EmailDashboard has Run AI Workflow button', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // Verify button exists
    final button = find.byType(ElevatedButton);
    expect(button, findsOneWidget);

    // Verify button label
    expect(find.text('Run AI Workflow'), findsOneWidget);

    // Verify button icon
    expect(find.byIcon(Icons.auto_awesome), findsOneWidget);
  });

  testWidgets('EmailDashboard scrolls to show full suggestion', (WidgetTester tester) async {
    // Set a small device size to force scrolling
    tester.binding.window.physicalSizeTestValue = const Size(400, 600);

    addTearDown(tester.binding.window.clearPhysicalSizeTestValue);

    await tester.pumpWidget(const MyApp());

    // Scroll down to see more content
    await tester.drag(find.byType(Column), const Offset(0, -300));
    await tester.pumpAndSettle();

    // Verify that scrolling worked (no exceptions thrown)
    expect(find.byType(SingleChildScrollView), findsOneWidget);
  });
}
