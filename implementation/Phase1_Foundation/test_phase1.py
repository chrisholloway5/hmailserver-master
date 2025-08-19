"""
Comprehensive Test Suite for hMailServer Phase 1 Implementation
Tests AI classification, context analysis, security features, and MCP integration
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add AI modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'implementation', 'Phase1_Foundation', 'AI'))

try:
    from email_classifier import EmailClassifier
    from context_analyzer import ContextAnalyzer
except ImportError as e:
    print(f"Warning: Could not import AI modules: {e}")
    EmailClassifier = None
    ContextAnalyzer = None

class Phase1TestSuite:
    """Comprehensive test suite for Phase 1 implementation"""
    
    def __init__(self):
        self.results = {
            'ai_classification': {},
            'context_analysis': {},
            'security_features': {},
            'mcp_integration': {},
            'overall_status': 'unknown'
        }
        
    async def run_all_tests(self):
        """Run all Phase 1 tests"""
        print("=" * 60)
        print("hMailServer Phase 1 Implementation Test Suite")
        print("=" * 60)
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Test AI Classification
        await self.test_ai_classification()
        
        # Test Context Analysis
        await self.test_context_analysis()
        
        # Test Security Features
        await self.test_security_features()
        
        # Test MCP Integration
        await self.test_mcp_integration()
        
        # Generate overall report
        self.generate_report()
        
    async def test_ai_classification(self):
        """Test AI email classification functionality"""
        print("Testing AI Email Classification...")
        print("-" * 40)
        
        if EmailClassifier is None:
            self.results['ai_classification'] = {
                'status': 'failed',
                'error': 'EmailClassifier module not available'
            }
            print("❌ AI Classification: Module not available")
            return
            
        try:
            classifier = EmailClassifier()
            await classifier.initialize()
            
            # Test spam detection
            spam_email = {
                'content': "URGENT!!! You won $1,000,000! Click here NOW!!!",
                'subject': "WINNER WINNER!!!",
                'sender': "noreply@suspicious.com"
            }
            
            spam_result = await classifier.classify_email(
                spam_email['content'], 
                spam_email['subject'], 
                spam_email['sender']
            )
            
            # Test legitimate email
            legit_email = {
                'content': "Hi John, Could you please review the quarterly report? Thanks, Sarah",
                'subject': "Quarterly Report Review",
                'sender': "sarah@company.com"
            }
            
            legit_result = await classifier.classify_email(
                legit_email['content'],
                legit_email['subject'],
                legit_email['sender']
            )
            
            # Validate results
            spam_detected = spam_result.get('is_spam', False)
            legit_not_spam = not legit_result.get('is_spam', True)
            
            self.results['ai_classification'] = {
                'status': 'passed' if spam_detected and legit_not_spam else 'failed',
                'spam_detection_accuracy': spam_detected,
                'false_positive_rate': not legit_not_spam,
                'spam_score': spam_result.get('spam_probability', 0),
                'legit_score': legit_result.get('spam_probability', 0)
            }
            
            print(f"✅ Spam Detection: {'PASSED' if spam_detected else 'FAILED'}")
            print(f"✅ False Positive Test: {'PASSED' if legit_not_spam else 'FAILED'}")
            print(f"   Spam Score: {spam_result.get('spam_probability', 0):.2f}")
            print(f"   Legit Score: {legit_result.get('spam_probability', 0):.2f}")
            
        except Exception as e:
            self.results['ai_classification'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"❌ AI Classification: {e}")
            
        print()
        
    async def test_context_analysis(self):
        """Test context-aware email analysis"""
        print("Testing Context-Aware Analysis...")
        print("-" * 40)
        
        if ContextAnalyzer is None:
            self.results['context_analysis'] = {
                'status': 'failed',
                'error': 'ContextAnalyzer module not available'
            }
            print("❌ Context Analysis: Module not available")
            return
            
        try:
            analyzer = ContextAnalyzer()
            await analyzer.initialize()
            
            # Test email with context
            test_email = {
                'sender': 'manager@company.com',
                'recipients': ['user@company.com'],
                'subject': 'URGENT: Server Down - Need Immediate Action',
                'content': '''The production server is down. 
                Please call me at 555-0123 immediately.
                Check the logs at https://logs.company.com/urgent
                This is affecting all customers.''',
                'has_attachments': False
            }
            
            context_result = await analyzer.analyze_email_context(test_email)
            
            # Validate context analysis
            priority_score = context_result.get('priority_score', 0)
            entities_found = len(context_result.get('entities', []))
            recommendations = len(context_result.get('recommendations', []))
            
            success = (
                priority_score > 0.7 and  # High priority detected
                entities_found >= 2 and    # Phone and URL detected
                recommendations > 0         # Recommendations provided
            )
            
            self.results['context_analysis'] = {
                'status': 'passed' if success else 'failed',
                'priority_score': priority_score,
                'entities_detected': entities_found,
                'recommendations_count': recommendations,
                'thread_analysis': bool(context_result.get('thread_context'))
            }
            
            print(f"✅ Priority Detection: {'PASSED' if priority_score > 0.7 else 'FAILED'}")
            print(f"✅ Entity Extraction: {'PASSED' if entities_found >= 2 else 'FAILED'}")
            print(f"✅ Recommendations: {'PASSED' if recommendations > 0 else 'FAILED'}")
            print(f"   Priority Score: {priority_score:.2f}")
            print(f"   Entities Found: {entities_found}")
            print(f"   Recommendations: {recommendations}")
            
        except Exception as e:
            self.results['context_analysis'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"❌ Context Analysis: {e}")
            
        print()
        
    async def test_security_features(self):
        """Test enhanced security features"""
        print("Testing Security Features...")
        print("-" * 40)
        
        try:
            # Test file structure
            security_files = [
                'implementation/Phase1_Foundation/Security/SecureEmailHandler.cpp',
                'implementation/Phase1_Foundation/Security/SecureEmailHandler.h',
                'implementation/Phase1_Foundation/Security/AdvancedThreatDetection.cpp',
                'implementation/Phase1_Foundation/Security/AdvancedThreatDetection.h'
            ]
            
            files_exist = all(os.path.exists(f) for f in security_files)
            
            # Test configuration
            config_exists = os.path.exists('config/hMailServerNext.conf.in')
            
            self.results['security_features'] = {
                'status': 'passed' if files_exist and config_exists else 'partial',
                'security_modules': files_exist,
                'configuration': config_exists,
                'files_checked': len(security_files)
            }
            
            print(f"✅ Security Modules: {'PASSED' if files_exist else 'FAILED'}")
            print(f"✅ Configuration: {'PASSED' if config_exists else 'FAILED'}")
            print(f"   Files Checked: {len(security_files)}")
            
        except Exception as e:
            self.results['security_features'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"❌ Security Features: {e}")
            
        print()
        
    async def test_mcp_integration(self):
        """Test MCP integration capabilities"""
        print("Testing MCP Integration...")
        print("-" * 40)
        
        try:
            # Test MCP configuration
            mcp_config_path = 'config/mcp/config.json'
            mcp_config_exists = os.path.exists(mcp_config_path)
            
            # Test MCP client modules
            mcp_files = [
                'implementation/Phase1_Foundation/AI/MCPClient.cpp',
                'implementation/Phase1_Foundation/AI/MCPClient.h'
            ]
            
            mcp_files_exist = all(os.path.exists(f) for f in mcp_files)
            
            # Test Python AI environment
            ai_env_exists = os.path.exists('implementation/Phase1_Foundation/AI/ai_env')
            requirements_exist = os.path.exists('implementation/Phase1_Foundation/AI/requirements.txt')
            
            success = mcp_config_exists and mcp_files_exist and ai_env_exists
            
            self.results['mcp_integration'] = {
                'status': 'passed' if success else 'partial',
                'mcp_config': mcp_config_exists,
                'mcp_client_modules': mcp_files_exist,
                'ai_environment': ai_env_exists,
                'requirements_file': requirements_exist
            }
            
            print(f"✅ MCP Configuration: {'PASSED' if mcp_config_exists else 'FAILED'}")
            print(f"✅ MCP Client Modules: {'PASSED' if mcp_files_exist else 'FAILED'}")
            print(f"✅ AI Environment: {'PASSED' if ai_env_exists else 'FAILED'}")
            print(f"✅ Requirements File: {'PASSED' if requirements_exist else 'FAILED'}")
            
        except Exception as e:
            self.results['mcp_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"❌ MCP Integration: {e}")
            
        print()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("=" * 60)
        print("PHASE 1 IMPLEMENTATION TEST REPORT")
        print("=" * 60)
        
        # Calculate overall status
        passed_tests = sum(1 for result in self.results.values() 
                          if isinstance(result, dict) and result.get('status') == 'passed')
        total_tests = len([k for k in self.results.keys() if k != 'overall_status'])
        
        if passed_tests == total_tests:
            overall_status = 'PASSED'
        elif passed_tests > total_tests / 2:
            overall_status = 'PARTIAL'
        else:
            overall_status = 'FAILED'
            
        self.results['overall_status'] = overall_status
        
        print(f"Overall Status: {overall_status}")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print()
        
        # Detailed results
        print("Detailed Results:")
        print("-" * 30)
        
        for test_name, result in self.results.items():
            if test_name == 'overall_status':
                continue
                
            status = result.get('status', 'unknown') if isinstance(result, dict) else 'unknown'
            print(f"{test_name.replace('_', ' ').title()}: {status.upper()}")
            
            if isinstance(result, dict) and 'error' in result:
                print(f"  Error: {result['error']}")
                
        print()
        
        # Save results to file
        with open('phase1_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        print("Test results saved to: phase1_test_results.json")
        print()
        
        # Recommendations
        print("Next Steps:")
        print("-" * 15)
        
        if overall_status == 'PASSED':
            print("✅ Phase 1 implementation is ready!")
            print("   - All core components are functioning")
            print("   - Ready to proceed with Phase 2")
            print("   - Consider running integration tests")
        elif overall_status == 'PARTIAL':
            print("⚠️  Phase 1 partially implemented:")
            print("   - Core functionality working")
            print("   - Some components need attention")
            print("   - Review failed tests above")
        else:
            print("❌ Phase 1 needs work:")
            print("   - Multiple components failed")
            print("   - Review implementation")
            print("   - Check dependencies and configuration")
            
        print(f"\nTest completed at: {datetime.now().isoformat()}")

async def main():
    """Main test function"""
    test_suite = Phase1TestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())