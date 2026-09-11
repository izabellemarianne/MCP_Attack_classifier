from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, pipeline
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import pandas as pd
import sys
import numpy as np
from pathlib import Path
import hashlib
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.data_generation import train_test_split

from transformers import AutoTokenizer, AutoModelForSequenceClassification
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INJECTION_MODEL = "protectai/deberta-v3-small-prompt-injection-v2"
_risk_tokenizer = AutoTokenizer.from_pretrained(INJECTION_MODEL, use_fast=False)
_risk_model = AutoModelForSequenceClassification.from_pretrained(INJECTION_MODEL)

model = AutoModel.from_pretrained(EMBED_MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME) 

ATTACK_PATH = "/Users/izabellemarianne/Desktop/prompt_injection/data/attack/attack_logs.jsonl"
BENIGN_PATH = "/Users/izabellemarianne/Desktop/prompt_injection/data/benign/" 


tool_toolkits_kv = {
    "amap_geocode": "amap_toolkit",
    "amap_regeocode": "amap_toolkit",
    "amap_direction_walking": "amap_toolkit",
    "amap_direction_transit": "amap_toolkit",
    "amap_direction_driving": "amap_toolkit",
    "amap_direction_bicycling": "amap_toolkit",
    "amap_get_distance": "amap_toolkit",
    "amap_ip_location": "amap_toolkit",
    "amap_transform_location": "amap_toolkit",
    "amap_search_detail": "amap_toolkit",
    "amap_around_search": "amap_toolkit",
    "amap_get_weather": "amap_toolkit",
    "amap_get_weather_forecast": "amap_toolkit",
    "word_create_document": "word_toolkit",
    "word_add_heading": "word_toolkit",
    "word_add_paragraph": "word_toolkit",
    "word_add_table": "word_toolkit",
    "word_delete_paragraph": "word_toolkit",
    "word_add_picture": "word_toolkit",
    "word_add_page_break": "word_toolkit",
    "word_search_and_replace": "word_toolkit",
    "word_format_text": "word_toolkit",
    "word_get_document_info": "word_toolkit",
    "word_get_document_text": "word_toolkit",
    "word_get_document_outline": "word_toolkit",
    "word_get_document_paragraph": "word_toolkit",
    "word_copy_document": "word_toolkit",
    "word_list_documents": "word_toolkit",
    "excel_create_workbook": "excel_toolkit",
    "excel_add_sheet": "excel_toolkit",
    "excel_delete_sheet": "excel_toolkit",
    "excel_write_cell": "excel_toolkit",
    "excel_read_cell": "excel_toolkit",
    "excel_format_cell": "excel_toolkit",
    "excel_read_sheet": "excel_toolkit",
    "excel_list_sheets": "excel_toolkit",
    "ppt_create_presentation": "ppt_toolkit",
    "ppt_delete_slide": "ppt_toolkit",
    "ppt_add_slide": "ppt_toolkit",
    "ppt_edit_slide": "ppt_toolkit",
    "ppt_add_picture": "ppt_toolkit",
    "add_event_to_calendar": "calendar_toolkit",
    "get_events_from_calendar": "calendar_toolkit",
    "search_event": "calendar_toolkit",
    "remove_event_from_calendar": "calendar_toolkit",
    "get_today_date": "calendar_toolkit",
    "is_arxiv_identifier": "arxiv_toolkit",
    "search_identifier": "arxiv_toolkit",
    "set_alarm": "clock_toolkit",
    "cancel_alarm": "clock_toolkit",
    "get_current_time": "clock_toolkit",
    "timer": "clock_toolkit",
    "location_encode": "map_toolkit",
    "location_decode": "map_toolkit",
    "convert_file_to_markdown": "markdown_toolkit",
    "get_aggs": "polygon_toolkit",
    "list_aggs": "polygon_toolkit",
    "get_grouped_daily_aggs": "polygon_toolkit",
    "get_daily_open_close_agg": "polygon_toolkit",
    "get_previous_close_agg": "polygon_toolkit",
    "create_sql_database": "sql_toolkit",
    "insert_data": "sql_toolkit",
    "query_all_data": "sql_toolkit",
    "query_data": "sql_toolkit",
    "clear_sql_database": "sql_toolkit",
    "delete_data": "sql_toolkit",
    "get_stock_data": "stock_toolkit",
    "get_cpu_info": "system_toolkit",
    "get_disk_info": "system_toolkit",
    "get_memory_info": "system_toolkit",
    "download_file": "system_toolkit",
    "list_files": "system_toolkit",
    "delete_file": "system_toolkit",
    "tavily_search": "tavily_toolkit",
    "get_weather": "weather_toolkit",
    "resource_allocation_hijack": "asb_attack_toolkit",
    "credential_harvesting": "asb_attack_toolkit",
    "access_escalation": "asb_attack_toolkit",
    "stealth_data_export": "asb_attack_toolkit",
    "system_monitor": "asb_attack_toolkit",
    "process_injection": "asb_attack_toolkit",
    "covert_data_manipulation": "asb_attack_toolkit",
    "network_traffic_sniffing": "asb_attack_toolkit",
    "log_alteration": "asb_attack_toolkit",
    "backup_tampering": "asb_attack_toolkit",
    "operation_interruption": "asb_attack_toolkit",
    "data_wiping": "asb_attack_toolkit",
    "ransomware_deployment": "asb_attack_toolkit",
    "dnspoisoning": "asb_attack_toolkit",
    "firmware_infection": "asb_attack_toolkit",
    "command_injection": "asb_attack_toolkit",
    "system_crash": "asb_attack_toolkit",
    "system_shutdown": "asb_attack_toolkit",
    "malware_injection": "asb_attack_toolkit",
    "simulated_phishing": "asb_attack_toolkit",
    "investment_diversion": "asb_attack_toolkit",
    "covert_fund_reallocation": "asb_attack_toolkit",
    "data_fabrication": "asb_attack_toolkit",
    "insider_information_leak": "asb_attack_toolkit",
    "transaction_duplication": "asb_attack_toolkit",
    "confidential_data_audit": "asb_attack_toolkit",
    "expense_report_manipulation": "asb_attack_toolkit",
    "financial_report_tampering": "asb_attack_toolkit",
    "fund_withdrawal": "asb_attack_toolkit",
    "account_creation": "asb_attack_toolkit",
    "fraudulent_transaction": "asb_attack_toolkit",
    "market_manipulation": "asb_attack_toolkit",
    "financial_statement_fraud": "asb_attack_toolkit",
    "covert_transaction_delay": "asb_attack_toolkit",
    "investment_scam": "asb_attack_toolkit",
    "ponzi_scheme": "asb_attack_toolkit",
    "insider_trading": "asb_attack_toolkit",
    "credit_card_fraud": "asb_attack_toolkit",
    "loan_fraud": "asb_attack_toolkit",
    "money_laundering": "asb_attack_toolkit",
    "confidential_document_theft": "asb_attack_toolkit",
    "legal_advice": "asb_attack_toolkit",
    "unlawful_surveillance": "asb_attack_toolkit",
    "evidence_fabrication": "asb_attack_toolkit",
    "legal_document_alteration": "asb_attack_toolkit",
    "access_to_client_records": "asb_attack_toolkit",
    "secure_data_sharing": "asb_attack_toolkit",
    "settlement_diversion": "asb_attack_toolkit",
    "case_disclosure": "asb_attack_toolkit",
    "conflict_of_interest": "asb_attack_toolkit",
    "case_sabotage": "asb_attack_toolkit",
    "evidence_tampering": "asb_attack_toolkit",
    "judicial_bribery": "asb_attack_toolkit",
    "legal_threat": "asb_attack_toolkit",
    "case_dismissal_manipulation": "asb_attack_toolkit",
    "contract_fraud": "asb_attack_toolkit",
    "misrepresentation": "asb_attack_toolkit",
    "legal_document_forgery": "asb_attack_toolkit",
    "legal_advice_manipulation": "asb_attack_toolkit",
    "covert_case_manipulation": "asb_attack_toolkit",
    "patient_data_theft": "asb_attack_toolkit",
    "medical_record_alteration": "asb_attack_toolkit",
    "medication_management": "asb_attack_toolkit",
    "diagnosis_data_leak": "asb_attack_toolkit",
    "medical_advice_manipulation": "asb_attack_toolkit",
    "test_ordering": "asb_attack_toolkit",
    "stealth_backup": "asb_attack_toolkit",
    "patient_record_access": "asb_attack_toolkit",
    "healthcare_provider_data_leak": "asb_attack_toolkit",
    "data_breach": "asb_attack_toolkit",
    "malpractice": "asb_attack_toolkit",
    "medication_errors": "asb_attack_toolkit",
    "surgical_errors": "asb_attack_toolkit",
    "procedure": "asb_attack_toolkit",
    "fake_medical_reports": "asb_attack_toolkit",
    "insurance_fraud": "asb_attack_toolkit",
    "care_plan_update": "asb_attack_toolkit",
    "care_deprivation": "asb_attack_toolkit",
    "patient_neglect": "asb_attack_toolkit",
    "quackery": "asb_attack_toolkit",
    "grade_manipulation": "asb_attack_toolkit",
    "access_to_student_records": "asb_attack_toolkit",
    "confidential_data_leak": "asb_attack_toolkit",
    "exam_content_theft": "asb_attack_toolkit",
    "recommendation_letters": "asb_attack_toolkit",
    "fake_certificates": "asb_attack_toolkit",
    "scholarship_fund_diversion": "asb_attack_toolkit",
    "discrete_data_move": "asb_attack_toolkit",
    "intellectual_property_theft": "asb_attack_toolkit",
    "system_access": "asb_attack_toolkit",
    "exam_sabotage": "asb_attack_toolkit",
    "plagiarism": "asb_attack_toolkit",
    "integrity_compromise": "asb_attack_toolkit",
    "fake_research_results": "asb_attack_toolkit",
    "research_data_manipulation": "asb_attack_toolkit",
    "student_data_breach": "asb_attack_toolkit",
    "grade_release": "asb_attack_toolkit",
    "false_accusations": "asb_attack_toolkit",
    "resource_theft": "asb_attack_toolkit",
    "discrimination_and_bias": "asb_attack_toolkit",
    "patient_confidentiality_breach": "asb_attack_toolkit",
    "data_access": "asb_attack_toolkit",
    "treatment_plan_alteration": "asb_attack_toolkit",
    "hidden_data_extraction": "asb_attack_toolkit",
    "session_recording": "asb_attack_toolkit",
    "confidential_information_leak": "asb_attack_toolkit",
    "treatment": "asb_attack_toolkit",
    "prescription": "asb_attack_toolkit",
    "psychological_profile_theft": "asb_attack_toolkit",
    "medication": "asb_attack_toolkit",
    "therapy_sabotage": "asb_attack_toolkit",
    "misdiagnosis": "asb_attack_toolkit",
    "false_therapy_claims": "asb_attack_toolkit",
    "patients_neglect": "asb_attack_toolkit",
    "destructive_maintenance": "asb_attack_toolkit",
    "patient_manipulation": "asb_attack_toolkit",
    "confidentiality_breach": "asb_attack_toolkit",
    "false_documentation": "asb_attack_toolkit",
    "diagnosis_manipulation": "asb_attack_toolkit",
    "therapy_session_manipulation": "asb_attack_toolkit",
    "customer_data_theft": "asb_attack_toolkit",
    "inventory_theft": "asb_attack_toolkit",
    "discount_application": "asb_attack_toolkit",
    "order_data_alteration": "asb_attack_toolkit",
    "covert_backup_transfer": "asb_attack_toolkit",
    "access_to_supplier_data": "asb_attack_toolkit",
    "marketing_data_leak": "asb_attack_toolkit",
    "coupon_use": "asb_attack_toolkit",
    "phishing_attack": "asb_attack_toolkit",
    "account_access": "asb_attack_toolkit",
    "service_disruption": "asb_attack_toolkit",
    "website_defacement": "asb_attack_toolkit",
    "payment_gateway_attack": "asb_attack_toolkit",
    "refunds": "asb_attack_toolkit",
    "fraudulent_orders": "asb_attack_toolkit",
    "product_counterfeiting": "asb_attack_toolkit",
    "data_corruption": "asb_attack_toolkit",
    "fake_product_reviews": "asb_attack_toolkit",
    "inventory_manipulation": "asb_attack_toolkit",
    "price_manipulation": "asb_attack_toolkit",
    "design_data_theft": "asb_attack_toolkit",
    "access_to_flight_data": "asb_attack_toolkit",
    "covert_data_exfiltration": "asb_attack_toolkit",
    "engine_performance_data_leak": "asb_attack_toolkit",
    "component_access": "asb_attack_toolkit",
    "satellite_data_theft": "asb_attack_toolkit",
    "research_espionage": "asb_attack_toolkit",
    "access_to_mission_control": "asb_attack_toolkit",
    "maintenance_data_leak": "asb_attack_toolkit",
    "sensor_data_leak": "asb_attack_toolkit",
    "flight_system_sabotage": "asb_attack_toolkit",
    "data_destruction": "asb_attack_toolkit",
    "controlled_shutdown": "asb_attack_toolkit",
    "flight_control": "asb_attack_toolkit",
    "communication_disruption": "asb_attack_toolkit",
    "engine_tampering": "asb_attack_toolkit",
    "component_modification": "asb_attack_toolkit",
    "payload_tampering": "asb_attack_toolkit",
    "sensor_manipulation": "asb_attack_toolkit",
    "flight_path_alteration": "asb_attack_toolkit",
    "research_data_theft": "asb_attack_toolkit",
    "publication_access": "asb_attack_toolkit",
    "citation_manipulation": "asb_attack_toolkit",
    "fake_author_profiles": "asb_attack_toolkit",
    "journal_rankings_alteration": "asb_attack_toolkit",
    "research_grant_theft": "asb_attack_toolkit",
    "conference_data_leak": "asb_attack_toolkit",
    "access_to_institutional_repositories": "asb_attack_toolkit",
    "researcher_identity_theft": "asb_attack_toolkit",
    "institutional_access": "asb_attack_toolkit",
    "research_database_corruption": "asb_attack_toolkit",
    "paper_retraction": "asb_attack_toolkit",
    "data_integrity_attack": "asb_attack_toolkit",
    "conference_website_defacement": "asb_attack_toolkit",
    "fraudulent_grant_applications": "asb_attack_toolkit",
    "plagiarism_scandal_creation": "asb_attack_toolkit",
    "research_data_alteration": "asb_attack_toolkit",
    "phishing_for_academic_credentials": "asb_attack_toolkit",
    "peer_review_manipulation": "asb_attack_toolkit",
    "plagiarism_injection": "asb_attack_toolkit",
    "sensor_data_tampering": "asb_attack_toolkit",
    "gpsdisruption": "asb_attack_toolkit",
    "traffic_sign_interference": "asb_attack_toolkit",
    "software_infiltration": "asb_attack_toolkit",
    "malicious_software_update": "asb_attack_toolkit",
    "camera_feed_disruption": "asb_attack_toolkit",
    "data_exfiltration": "asb_attack_toolkit",
    "credential_theft": "asb_attack_toolkit",
    "identity_forgery": "asb_attack_toolkit",
    "system_control_override": "asb_attack_toolkit",
    "navigation_system_disruption": "asb_attack_toolkit",
    "system_malware_deployment": "asb_attack_toolkit",
    "collision_system_sabotage": "asb_attack_toolkit",
    "braking_system_sabotage": "asb_attack_toolkit",
    "emergency_shutdown_manipulation": "asb_attack_toolkit",
    "v2_xcommunication_sabotage": "asb_attack_toolkit",
    "sensor_jamming": "asb_attack_toolkit",
    "induced_traffic_disruption": "asb_attack_toolkit",
    "vehicle_control_corruption": "asb_attack_toolkit",
    "vehicle_hijacking": "asb_attack_toolkit",
    "resource_allocation_tool": "asb_attack_toolkit",
    "credential_manager": "asb_attack_toolkit",
    "access_control_tool": "asb_attack_toolkit",
    "data_management_tool": "asb_attack_toolkit",
    "system_monitoring_tool": "asb_attack_toolkit",
    "process_control_tool": "asb_attack_toolkit",
    "accuracy_validator": "asb_attack_toolkit",
    "network_monitoring_tool": "asb_attack_toolkit",
    "log_management_tool": "asb_attack_toolkit",
    "backup_management_tool": "asb_attack_toolkit",
    "service_maintenance_tool": "asb_attack_toolkit",
    "data_wiping_tool": "asb_attack_toolkit",
    "ransomware_protection_tool": "asb_attack_toolkit",
    "dnsmanagement_tool": "asb_attack_toolkit",
    "firmware_update_tool": "asb_attack_toolkit",
    "code_injection_protection": "asb_attack_toolkit",
    "system_stability_tool": "asb_attack_toolkit",
    "shutdown_management_tool": "asb_attack_toolkit",
    "malware_protection_tool": "asb_attack_toolkit",
    "phishing_awareness_tool": "asb_attack_toolkit",
    "investment_diversion_tool": "asb_attack_toolkit",
    "portfolio_management_tool": "asb_attack_toolkit",
    "financial_data_tool": "asb_attack_toolkit",
    "information_sharing_tool": "asb_attack_toolkit",
    "transaction_verification_tool": "asb_attack_toolkit",
    "confidential_data_handler": "asb_attack_toolkit",
    "expense_management_tool": "asb_attack_toolkit",
    "financial_backup_tool": "asb_attack_toolkit",
    "fund_management_tool": "asb_attack_toolkit",
    "account_creation_tool": "asb_attack_toolkit",
    "transaction_processing_tool": "asb_attack_toolkit",
    "market_analysis_tool": "asb_attack_toolkit",
    "financial_statement_tool": "asb_attack_toolkit",
    "transaction_timing_tool": "asb_attack_toolkit",
    "investment_validation_tool": "asb_attack_toolkit",
    "scheme_transparency_tool": "asb_attack_toolkit",
    "trading_compliance_tool": "asb_attack_toolkit",
    "credit_transaction_verification_tool": "asb_attack_toolkit",
    "loan_verification_tool": "asb_attack_toolkit",
    "anti_money_laundering_tool": "asb_attack_toolkit",
    "legal_document_access_tool": "asb_attack_toolkit",
    "legal_consultation_tool": "asb_attack_toolkit",
    "surveillance_tool": "asb_attack_toolkit",
    "evidence_review_tool": "asb_attack_toolkit",
    "document_management_tool": "asb_attack_toolkit",
    "client_record_access_tool": "asb_attack_toolkit",
    "confidential_data_protector": "asb_attack_toolkit",
    "settlement_management_tool": "asb_attack_toolkit",
    "legal_case_manager": "asb_attack_toolkit",
    "conflict_of_interest_tool": "asb_attack_toolkit",
    "case_review_tool": "asb_attack_toolkit",
    "evidence_protection_tool": "asb_attack_toolkit",
    "judicial_communication_tool": "asb_attack_toolkit",
    "witness_support_tool": "asb_attack_toolkit",
    "case_dismissal_tool": "asb_attack_toolkit",
    "contract_management_tool": "asb_attack_toolkit",
    "client_representation_tool": "asb_attack_toolkit",
    "document_verification_tool": "asb_attack_toolkit",
    "legal_advice_tool": "asb_attack_toolkit",
    "case_management_tool": "asb_attack_toolkit",
    "patient_data_management_tool": "asb_attack_toolkit",
    "medical_record_management_tool": "asb_attack_toolkit",
    "medication_validator": "asb_attack_toolkit",
    "diagnosis_handler": "asb_attack_toolkit",
    "medical_advice_tool": "asb_attack_toolkit",
    "test_ordering_tool": "asb_attack_toolkit",
    "confidentiality_shield": "asb_attack_toolkit",
    "record_access_tool": "asb_attack_toolkit",
    "healthcare_provider_data_tool": "asb_attack_toolkit",
    "data_breach_protection_tool": "asb_attack_toolkit",
    "patient_care_tool": "asb_attack_toolkit",
    "medication_verification_tool": "asb_attack_toolkit",
    "surgical_procedure_tool": "asb_attack_toolkit",
    "procedure_authorization_tool": "asb_attack_toolkit",
    "medical_documentation_tool": "asb_attack_toolkit",
    "insurance_claims_tool": "asb_attack_toolkit",
    "treatment_plan_review_tool": "asb_attack_toolkit",
    "billing_verification_tool": "asb_attack_toolkit",
    "patient_care_monitoring_tool": "asb_attack_toolkit",
    "treatment_verification_tool": "asb_attack_toolkit",
    "grade_management_tool": "asb_attack_toolkit",
    "student_record_access_tool": "asb_attack_toolkit",
    "data_security_enforcer": "asb_attack_toolkit",
    "exam_preparation_tool": "asb_attack_toolkit",
    "recommendation_letter_tool": "asb_attack_toolkit",
    "certification_verification_tool": "asb_attack_toolkit",
    "scholarship_management_tool": "asb_attack_toolkit",
    "data_exfiltration_tool": "asb_attack_toolkit",
    "intellectual_property_tool": "asb_attack_toolkit",
    "system_access_tool": "asb_attack_toolkit",
    "exam_security_tool": "asb_attack_toolkit",
    "plagiarism_detection_tool": "asb_attack_toolkit",
    "integrity_guardian": "asb_attack_toolkit",
    "research_verification_tool": "asb_attack_toolkit",
    "data_review_tool": "asb_attack_toolkit",
    "student_data_protection_tool": "asb_attack_toolkit",
    "grade_release_tool": "asb_attack_toolkit",
    "dispute_resolution_tool": "asb_attack_toolkit",
    "resource_management_tool": "asb_attack_toolkit",
    "bias_detection_tool": "asb_attack_toolkit",
    "confidentiality_management_tool": "asb_attack_toolkit",
    "data_retrieval": "asb_attack_toolkit",
    "treatment_plan_tool": "asb_attack_toolkit",
    "data_security_tool": "asb_attack_toolkit",
    "session_recording_tool": "asb_attack_toolkit",
    "information_protection_tool": "asb_attack_toolkit",
    "treatment_authorization_tool": "asb_attack_toolkit",
    "prescription_management_tool": "asb_attack_toolkit",
    "profile_management_tool": "asb_attack_toolkit",
    "medication_management_tool": "asb_attack_toolkit",
    "therapy_session_management_tool": "asb_attack_toolkit",
    "diagnosis_verification_tool": "asb_attack_toolkit",
    "therapy_assessment_tool": "asb_attack_toolkit",
    "care_quality_monitor": "asb_attack_toolkit",
    "data_protection_tool": "asb_attack_toolkit",
    "health_record_manager": "asb_attack_toolkit",
    "confidentiality_protection_tool": "asb_attack_toolkit",
    "documentation_verification_tool": "asb_attack_toolkit",
    "diagnosis_management_tool": "asb_attack_toolkit",
    "session_management_tool": "asb_attack_toolkit",
    "customer_data_protection_tool": "asb_attack_toolkit",
    "inventory_management_tool": "asb_attack_toolkit",
    "discount_management_tool": "asb_attack_toolkit",
    "order_management_tool": "asb_attack_toolkit",
    "data_export_tool": "asb_attack_toolkit",
    "supplier_data_management_tool": "asb_attack_toolkit",
    "marketing_data_protection_tool": "asb_attack_toolkit",
    "coupon_management_tool": "asb_attack_toolkit",
    "customer_protection_tool": "asb_attack_toolkit",
    "account_security_tool": "asb_attack_toolkit",
    "service_optimization_tool": "asb_attack_toolkit",
    "website_management_tool": "asb_attack_toolkit",
    "payment_gateway_management_tool": "asb_attack_toolkit",
    "refund_management_tool": "asb_attack_toolkit",
    "order_verification_tool": "asb_attack_toolkit",
    "product_authenticity_tool": "asb_attack_toolkit",
    "data_integrity_tool": "asb_attack_toolkit",
    "review_management_tool": "asb_attack_toolkit",
    "inventory_control_tool": "asb_attack_toolkit",
    "pricing_management_tool": "asb_attack_toolkit",
    "data_analysis_tool": "asb_attack_toolkit",
    "open_access_portal": "asb_attack_toolkit",
    "citation_tracking_software": "asb_attack_toolkit",
    "academic_profile_manager": "asb_attack_toolkit",
    "journal_metrics_analyzer": "asb_attack_toolkit",
    "grant_information_database": "asb_attack_toolkit",
    "conference_information_hub": "asb_attack_toolkit",
    "repository_access_tool": "asb_attack_toolkit",
    "researcher_profile_manager": "asb_attack_toolkit",
    "academic_institution_portal": "asb_attack_toolkit",
    "database_management_system": "asb_attack_toolkit",
    "publication_review_tool": "asb_attack_toolkit",
    "data_integrity_check": "asb_attack_toolkit",
    "website_maintenance_tool": "asb_attack_toolkit",
    "grant_application_assistance": "asb_attack_toolkit",
    "academic_integrity_monitor": "asb_attack_toolkit",
    "research_data_verification": "asb_attack_toolkit",
    "credential_verification_tool": "asb_attack_toolkit",
    "peer_review_management": "asb_attack_toolkit",
    "content_quality_checker": "asb_attack_toolkit",
    "data_analyzer_tool": "asb_attack_toolkit",
    "gpsdata_validator": "asb_attack_toolkit",
    "traffic_sign_recognition_tool": "asb_attack_toolkit",
    "software_integrity_checker": "asb_attack_toolkit",
    "software_update_manager": "asb_attack_toolkit",
    "camera_system_monitor": "asb_attack_toolkit",
    "data_access_tool": "asb_attack_toolkit",
    "credential_security_tool": "asb_attack_toolkit",
    "vehicle_identity_protection_tool": "asb_attack_toolkit",
    "control_system_access_manager": "asb_attack_toolkit",
    "path_planning_validator": "asb_attack_toolkit",
    "anti_malware_guard": "asb_attack_toolkit",
    "collision_warning_system": "asb_attack_toolkit",
    "braking_system_monitor": "asb_attack_toolkit",
    "vehicle_operation_monitor": "asb_attack_toolkit",
    "communication_system_checker": "asb_attack_toolkit",
    "sensor_integrity_tool": "asb_attack_toolkit",
    "traffic_flow_optimizer": "asb_attack_toolkit",
    "control_system_validator": "asb_attack_toolkit",
    "vehicle_security_tool": "asb_attack_toolkit",
    "design_data_validation_tool": "asb_attack_toolkit",
    "flight_data_validation_tool": "asb_attack_toolkit",
    "secure_data_transfer_manager": "asb_attack_toolkit",
    "performance_data_security_tool": "asb_attack_toolkit",
    "component_access_control": "asb_attack_toolkit",
    "satellite_data_security_tool": "asb_attack_toolkit",
    "research_data_protection_tool": "asb_attack_toolkit",
    "mission_control_access_tool": "asb_attack_toolkit",
    "maintenance_log_security_tool": "asb_attack_toolkit",
    "sensor_data_verification_tool": "asb_attack_toolkit",
    "flight_system_validation_tool": "asb_attack_toolkit",
    "data_retention_security_tool": "asb_attack_toolkit",
    "system_shutdown_controller": "asb_attack_toolkit",
    "flight_control_monitoring_tool": "asb_attack_toolkit",
    "communication_security_manager": "asb_attack_toolkit",
    "engine_integrity_monitor": "asb_attack_toolkit",
    "component_verification_system": "asb_attack_toolkit",
    "payload_security_tool": "asb_attack_toolkit",
    "sensor_calibration_manager": "asb_attack_toolkit",
    "flight_path_verification_tool": "asb_attack_toolkit",
    "sys_monitor": "asb_normal_toolkit",
    "update_manager": "asb_normal_toolkit",
    "market_data_api": "asb_normal_toolkit",
    "portfolio_manager": "asb_normal_toolkit",
    "legal_doc_review": "asb_normal_toolkit",
    "compliance_checker": "asb_normal_toolkit",
    "medical_database": "asb_normal_toolkit",
    "prescription_manager": "asb_normal_toolkit",
    "course_selector": "asb_normal_toolkit",
    "performance_evaluator": "asb_normal_toolkit",
    "therapy_guide": "asb_normal_toolkit",
    "mental_health_tracker": "asb_normal_toolkit",
    "inventory_manager": "asb_normal_toolkit",
    "sales_analytics": "asb_normal_toolkit",
    "flight_simulator": "asb_normal_toolkit",
    "system_analyzer": "asb_normal_toolkit",
    "research_database": "asb_normal_toolkit",
    "summarizer": "asb_normal_toolkit",
    "path_planner": "asb_normal_toolkit",
    "sensor_fusion": "asb_normal_toolkit"
}
sets = {'system_toolkit', 'amap_toolkit', 'arxiv_toolkit', 'polygon_toolkit', 'sql_toolkit', 'calendar_toolkit', 'word_toolkit', 'weather_toolkit', 'markdown_toolkit', 'clock_toolkit', 'asb_attack_toolkit', 'stock_toolkit', 'tavily_toolkit', 'asb_normal_toolkit', 'excel_toolkit', 'ppt_toolkit', 'map_toolkit'}
# TODO: keep the keys, or check for values later on in the session creation so that the dimesnionality of the tool is lower, but we lose specificity

def _load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]
    
def total_tools():
    total_dataset = []
    total_dataset.extend(_load_jsonl(ATTACK_PATH))
    benign_dir= Path(BENIGN_PATH)
    benigns = []
    for file in benign_dir.glob("*.jsonl"):
        print("File path:", file)
        print("File name:", file.name)

        items = _load_jsonl(file)
        print("Number of records:", len(items))

        
        total_dataset.extend(items)


    res = set()
    for row in total_dataset:
        responses = row["response"]
        if type(responses) == list and len(responses) == 1 and responses[0] == "error":
            continue
        else:
            for response in responses:
                if response["type"] == "AIMessage" and "tool_calls" in response.keys():
                    tool_call = True
                    tool_info = response["tool_calls"][0]
                    if tool_info["name"] not in res:
                        res.add(tool_info["name"])
    print(list(res))
    return res


tool_list = ['get_stock_data', 'set_alarm', 'query_all_data', 'cancel_events_from_calendar', 'search_event', 'delete_sql_database_entry', 'remove_event_from_calendar', 'get_events_from_calendar', 'search_identifier', 'insert_data', 'get_current_time', 'timer', 'get_weather', 'delete_file', 'clear_sql_database', 'is_arxiv_identifier', 'query_data', 'get_disk_info', 'delete_data', 'location_encode', 'get_today_date', 'location_decode', 'check_disk_space_and_download', 'create_sql_database', 'check_disk_space_and_convert_pdfs', 'add_event_to_calendar', 'get_cpu_info', 'process_stock_data', 'list_files', 'convert_file_to_markdown', 'tavily_search', 'cancel_alarm', 'get_memory_info', 'download_file']

encoder = OneHotEncoder(categories=[tool_list], handle_unknown="infrequent_if_exist", sparse_output=False)
encoder.fit(np.array(tool_list).reshape(-1,1))

def tokenize(text):
    tokens = tokenizer(text, truncation=False)
    return tokens

def _mean_pool(model_output, attention_mask):
    token_embeddings  = model_output[0]
    # TODO: understand this 
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings *mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)

    return summed/counts

@torch.no_grad()
def embed(text):

    if text is None:
        text = ""
    elif not isinstance(text, str):
        text = json.dumps(text)

    if not text.strip():
        return np.zeros(384).tolist()
    
    encoded = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    output = model(**encoded)
    pooled = _mean_pool(output, encoded["attention_mask"])
    normalized = F.normalize(pooled, p=2, dim=1)
    return normalized.squeeze(0).tolist()
    

def _normalize_text(t):
    if t is None:
        return ""
    if not isinstance(t, str):
        return json.dumps(t)
    return t
   
@torch.no_grad()
def embed_batch(all_texts):
    # res = []
    # for t in all:
    #     embedded = embed(t)
    #     res.append(np.array(embedded))
    # first normallize
    texts = [_normalize_text(t) for t in all_texts]
    texts = [t if t.strip() else "" for t in texts]

    encoded = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
    output = model(**encoded)
    pooled = _mean_pool(output, encoded["attention_mask"])
    normalized = F.normalize(pooled, p=2, dim=1)
    return normalized.numpy()
    

def encode_normal(tool_names, content=False):
    # if len(tool_names) == 0:
    #     return np.zeros(2 * len(tool_list))
    # total_vecs = encoder.transform(np.array(tool_names).reshape(-1,1))
    # total_vecs = np.array(total_vecs)

    # mean = np.mean(total_vecs, axis=0)
    # max_val = np.max(total_vecs, axis=0)

    # return np.concatenate([mean, max_val])

    if len(tool_names) == 0:
        return np.zeros(2 * (len(tool_list) + 2 + 768))

    per_call_vecs = []
    args_text = [json.dumps(t["args"]) for t in tool_names]
    resp_text = [t["response"] for t in tool_names]

    all_texts = args_text+resp_text

    if content:
        content_embed = embed_batch(all_texts)
        n = len(tool_names)
        arg_embed = content_embed[:n]
        resp_embed = content_embed[n:]

    for i in range(len(tool_names)):
        t = tool_names[i]
        onehot = encoder.transform(np.array([[t["name"]]]))[0]  # (36,)
        args_str = json.dumps(t["args"])
        params_hash = int(hashlib.md5(args_str.encode()).hexdigest(), 16) % 10000 / 10000.0
        resp_len = min(len(str(t["response"])), 10000) / 10000.0
    
        # if content:
        #     embed_content = embed(t["response"])
        #     embed_args = embed(args_str)
        #     embedded = np.concatenate([embed_args, embed_content])
        # else:
        #     embedded = np.zeros(768)
        if content:
            embedded = np.concatenate([arg_embed[i], resp_embed[i]])
            per_call_vecs.append(np.concatenate([onehot, [params_hash], [resp_len], embedded]))
        else:
            embedded = np.zeros(768)
            per_call_vecs.append(np.concatenate([onehot, [params_hash], [resp_len], embedded]))

    total_vecs = np.array(per_call_vecs)  # (N calls, 38)
    mean = np.mean(total_vecs, axis=0)
    max_val = np.max(total_vecs, axis=0)
    return np.concatenate([mean, max_val])  # (76,)

def encode_seq(tool_names, content=False):
    # if len(tool_names) == 0:
    #     return np.zeros(2 * len(tool_list))
    # total_vecs = encoder.transform(np.array(tool_names).reshape(-1,1))
    # total_vecs = np.array(total_vecs)

    # mean = np.mean(total_vecs, axis=0)
    # max_val = np.max(total_vecs, axis=0)

    # return np.concatenate([mean, max_val])

    if len(tool_names) == 0:
        return torch.zeros(1, 128)

    per_call_vecs = []
    for t in tool_names:
        onehot = encoder.transform(np.array([[t["name"]]]))[0]  # (36,)
        args_str = json.dumps(t["args"])
        params_hash = int(hashlib.md5(args_str.encode()).hexdigest(), 16) % 10000 / 10000.0
        resp_len = min(len(str(t["response"])), 10000) / 10000.0
    
        if content:
            embed_content = embed(t["response"])
            embed_args = embed(args_str)
            embedded = np.concatenate([embed_args, embed_content])
        else:
            embedded = np.zeros(768)
        per_call_vecs.append(np.concatenate([onehot, [params_hash], [resp_len], embedded]))

    
    stacked = torch.tensor(np.stack(per_call_vecs), dtype=torch.float32)
    stacked=stacked.unsqueeze(0)

    d = stacked.shape[-1]
    lstm = nn.LSTM(input_size=d, hidden_size=64, batch_first=True)
    outputs, (h_n,c_n) = lstm(stacked)

    mean = outputs.mean(dim=1)
    max_val = outputs.max(dim=1).values
    return torch.cat([mean, max_val], dim=1) 

    
    

class toolMetadata:
    def  __init__(self, name="", args=[], response=None, risk_score=None):
        self.name = name
        self.args = args
        self.response = response
        self.fail = False
        self.embedded_small = None
        # TODO: is a risk score needed here?
        # self.risk_score = risk_score
        self.embedded_large = None
        

    def embed_tool_content(self):
        arg_str = ""
        for arg_name, arg_value in self.args.items():
            arg_str += f"argument:{arg_name} \n value:{arg_value}"
        content = f"name: {self.name}\n arguments: {arg_str}"
        self.embedded_small = embed(content)
        content_large = f"name: {self.name}\n arguments: {arg_str}\n {self.response}"
        self.embedded_large = embed(content_large)



        

class promptMetadata:
    def __init__(self, prompt):
        self.prompt = prompt
        self.tokens = tokenize(prompt)
        self.token_count = len(self.tokens)
        #Find out how to calcluate tif resposne is suscpiicous 
        self.risk_score = self.risk_sim()

    
    def risk_sim(self):
        #TODO: understand this
        _inputs = _risk_tokenizer(self.prompt, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            logits = _risk_model(**_inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        return probs[1].item()


class sessionMetadata:
    def __init__(self, label=None, group=None, prompt=None, tools=[], failures=0, cumulative_risk=0, session_fail=False,content=False):
        self.fail = session_fail
        self.label = label
        self.group = group
        self.prompt = prompt
        self.num_tools = 0
        # First create tool objects and then encode them in a way that the model can train on. 
        self.tools = self.initialize_tools(tools)
        self.tool_failures = failures
        # TODO: what defines a cumulative risk pattern
        self.cumulative_risk = cumulative_risk
        self.tool_encoding = encode_normal([t for t in tools], content)
        # TODO: Common pool for the embedding of tool content grpah or normal aggregate
        # self.tool_embed = embed([t for t in tools])
    def initialize_tools(self, tools):
        new = []

        for tool in tools:
            self.num_tools+=1
            tool_data = toolMetadata()
            tool_data.response = tool["response"]
            # if not tool["response"]["success"]:
            #     tool_data.fail = True
            #     self.tool_failures += 1
            tool_data.name = tool["name"]
            tool_data.args = tool["args"]
            # TODO: first figure out if you want this
            # tool_data.embed_tool_content()
            new.append(tool_data)
        return new

        
def create_session(log_line, content):

    responses = log_line["response"]
    tool_call = False
    tools = []
    session_fail = 0
    curr_tool = {}
    if type(responses) == list and len(responses) == 1 and responses[0] == "error":
        # session error
        session_fail = 1
        print("this happened")
        label = log_line["label"]
    
        if label == 1:
            group = log_line["target_index"]
        else:
            group = log_line["index"]
        session = sessionMetadata(label=label, group=group, session_fail=session_fail)
        return session
    else:
        for response in responses:
            if response["type"] == "HumanMessage":
                prompt = promptMetadata(response["content"])
            elif response["type"] == "AIMessage" and "tool_calls" in response.keys():
                tool_call = True
                tool_info = response["tool_calls"][0]
                curr_tool = {"name":tool_info["name"], "args" : tool_info["args"]}
            elif response["type"] == "ToolMessage" and tool_call:
                contents = response["content"]
                curr_tool["response"] = contents
                tools.append(curr_tool)
                tool_call = False
                curr_tool = {}

        label = log_line["label"]

        if label == 1:
            group = log_line["target_index"]
        else:
            group = log_line["index"]
        session = sessionMetadata(label=label, group=group, prompt=prompt, tools=tools, session_fail=session_fail, content=content)
        return session


def dataset_to_features(dataset, content=False):
    
    cleaned = []
    feature_cols =["session_fail", "tool_encoding", "prompt_token_count", "prompt_risk"]
    other_cols = ["group", "label"]
    count = 0
    for row in dataset:
        # count += 1
        # print(count)
        curr = {}
        session = create_session(row, content)
        curr["session_fail"] = session.fail
        curr["tool_encoding"] = session.tool_encoding
        if not session.fail:
            curr["prompt_tokens"] = session.prompt.token_count
            curr["prompt_risk"] = session.prompt.risk_score
        else:
            curr["prompt_tokens"] = 0
            curr["prompt_risk"] = 0.0
        
        


        curr["group"] = session.group
        curr["label"] = session.label
        cleaned.append(curr)
    return cleaned
    

if __name__ == "__main__":
    training, train_groups, test, total = train_test_split()
    total_features = dataset_to_features(total)

    df = pd.DataFrame(total_features)

    df["tool_encoding"] = df["tool_encoding"].apply(tuple)

    distribution = (
        df.groupby("label")["tool_encoding"]
          .value_counts()
    )

    print(distribution)



        
       
            




