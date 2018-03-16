from collections import OrderedDict

# Hallmarks of cancer and roughly corresponding PubMed query terms.
# The keys are used in the UI and the values in the backend when
# querying for co-occurrences of user-provided terms with the
# hallmarks.

hocqueries = OrderedDict([
    ('invasion', 'Neoplasm Invasiveness[MeSH]'),
    ('metastasis', 'Neoplasm Metastasis[MeSH]'),
    ('immune response', 'Immune System Processes[MeSH]'),
    ('immunosuppression', 'Immunosuppression[MeSH]'),
    ('cellular energetics', 'Energy Metabolism[MeSH]'),
    ('glycolysis', 'Glycolysis[MeSH]'),
    ('warburg effect', '"Warburg effect"'),
    ('immortalization', '"immortalization"'),
    ('senescence', 'Cell Aging[MeSH]'),
    ('cell cycle', 'Cell Cycle[MeSH]'),
    ('cell cycle checkpoint', 'Cell Cycle Checkpoints[MeSH]'),
    ('contact inhibition', 'Contact Inhibition[MeSH]'),
    ('genomic instability', 'Genomic Instability[MeSH]'),
    ('DNA damage', 'DNA Damage[MeSH]'),
    ('DNA adduction', 'DNA Adducts[MeSH]'),
    ('DNA strand breaking', 'DNA Breaks[MeSH]'),
    ('DNA repair', 'DNA Repair[MeSH]'),
    ('mutation', 'Mutation[MeSH]'),
    ('angiogenesis', 'Neovascularization, Pathologic[MeSH]'),
    ('cell death', 'Cell Death[MeSH]'),
    ('apoptosis', 'Apoptosis[MeSH]'),
    ('autophagy', 'Autophagy[MeSH]'),
    ('necrosis', 'Necrosis[MeSH]'),
    ('proliferation', 'Cell Proliferation[MeSH]'),
    ('growth promoting signals', 'MAP Kinase Signaling System[MeSH]'),
    ('inflammation', 'Inflammation[MeSH]'),
    ('oxidative stress', 'Oxidative Stress[MeSH]'),
])
