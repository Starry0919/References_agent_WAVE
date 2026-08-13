from harness.paper_extraction.human_review_view import build_understanding,humanize_locator,machine_export,review_export

def test_locator_is_human_readable():
    assert humanize_locator('a_b_s_t_r_a_c_t_p001')=='Abstract'
    assert humanize_locator('2_3_mutation_on_glpk_p004')=='2 3 mutation on glpk'

def test_understanding_separates_epistemic_classes():
    view=build_understanding('GOLD-P01')
    assert view['title'].startswith('Adaptive laboratory evolution')
    assert view['paper_fact']['evidence_label']=='Abstract'
    assert view['agent_scientific_interpretation']['experiment_count']>0
    assert view['hypothesis']['value'] is None
    assert all(x['classification']=='AGENT_SCIENTIFIC_INTERPRETATION' for x in view['experiments'])

def test_curated_exports_are_role_isolated_and_machine_parseable():
    machine=machine_export('GOLD-P01','ANNOTATOR_A');review=review_export('GOLD-P01','ANNOTATOR_A')
    assert machine['schema'].endswith('.v3') and 'source_document_path' not in str(machine)
    assert review['reviewer']['role']=='ANNOTATOR_A' and review['schema'].endswith('.v3')
    assert 'ANNOTATOR_B' not in str(review)
