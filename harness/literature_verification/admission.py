def evaluate_admission(context:dict)->dict:
 gates={'contracts_compatible':bool(context.get('contracts_compatible')),'legal_bounded_acquisition':bool(context.get('legal_bounded_acquisition')),'production_parser_available':bool(context.get('production_parser_available')),'canonical_adapter_tested':bool(context.get('canonical_adapter_tested')),'verifier_safety_tests_pass':bool(context.get('verifier_safety_tests_pass')),'human_gold_complete':bool(context.get('human_gold_complete')),'identity_calibrated':bool(context.get('identity_calibrated')),'judge_calibrated':bool(context.get('judge_calibrated')),'regressions_clear':bool(context.get('regressions_clear')),'shadow_no_ddr_write':context.get('shadow_no_ddr_write') is True}
 blockers=[k for k,v in gates.items() if not v]
 if not gates['regressions_clear']:status='BLOCKED_REGRESSION'
 elif not gates['human_gold_complete'] or not gates['identity_calibrated'] or not gates['judge_calibrated']:status='HOLD_FOR_GOLD'
 elif not gates['production_parser_available']:status='HOLD_FOR_PARSER'
 elif blockers:status='SHADOW_ONLY'
 else:status='ADMIT'
 return {'status':status,'hard_gates':gates,'blockers':blockers,'risk_hierarchy':['FALSE_DIRECT_ADMISSION','FALSE_PDF_IDENTITY_ACCEPTANCE','FALSE_SUPPORTING_ADMISSION','MISSED_BORDERLINE_PAPER'],'warnings':[],'recommended_next_action':'Complete dual annotation/adjudication and run calibration before production admission.'}
