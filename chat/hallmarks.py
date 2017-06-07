from collections import OrderedDict

hallmark_codes = OrderedDict([
    ('1', 'INVASION AND METASTASIS'),
    ('11', 'invasion'),
    ('12', 'metastasis'),
    ('2', 'IMMUNE DESTRUCTION'),
    ('21', 'immune response'),
    ('22', 'immunosuppression'),
    ('3', 'CELLULAR ENERGETICS'),
    ('31', 'glycolysis/warburg effect'),
    ('4', 'REPLICATIVE IMMORTALITY'),
    ('41', 'immortalization'),
    ('42', 'senescence'),
    ('5', 'EVADING GROWTH SUPPRESSORS'),
    ('51', 'deregulating cc checkpoints'),
    ('511', 'deregulating--cell cycle'),
    ('52', 'evading contact inhibition'),
    ('6', 'GENOME INSTABILITY AND MUTATION'),
    ('61', 'DNA damage'),
    ('611', 'DNA adducts'),
    ('612', 'DNA strand breaks'),
    ('62', 'DNA repair'),
    ('63', 'mutation'),
    ('7', 'INDUCING ANGIOGENESIS'),
    ('71', 'deregulating angiogenesis'),
    ('711', 'angiogenic factors'),
    ('8', 'RESISTING CELL DEATH'),
    ('81', 'apoptosis'),
    ('82', 'autophagy'),
    ('83', 'necrosis'),
    ('9', 'SUSTAINING PROLIFERATIVE SIGNALING'),
    ('91', 'proliferative signaling--cell cycle'),
    ('92', 'growth signals'),
    ('921', 'growth signals--downstream signaling'),
    ('93', 'proliferative signaling--receptors'),
    ('x', 'TUMOR PROMOTING INFLAMMATION'),
    ('x1', 'immune response to inflammation'),
    ('x2', 'inflammation'),
    ('x21', 'oxidative stress'),
])

# Top level hallmarks have a single-character code
top_hallmark_codes = OrderedDict([
    (k, v) for k, v in hallmark_codes.items() if len(k) == 1
])

# Hallmark colors from Hanahan and Weinberg 2011
top_hallmark_colors = [
    '#221E1F',
    '#D1268C',
    '#813C96',
    '#007EB1',
    '#774401',
    '#1D3B96',
    '#F03B34',
    '#839098',
    '#019E5A',
    '#E17A1C',
]

# top_hallmark_colors with variants for subtypes
full_hallmark_colors = [
    '#221E1F',    # 1. invasion and metastasis
    '#221E1F',    # 1.1. invasion
    '#221E1F',    # 1.2. metastasis
    '#D1268C',    # 2. immune destruction
    '#D1268C',    # 2.1. immune response
    '#D1268C',    # 2.2. immunosuppression
    '#813C96',    # 3. cellular energetics
    '#813C96',    # 3.1. glycolysis/warburg effect
    '#007EB1',    # 4. replicative immortality
    '#007EB1',    # 4.1. immortalization
    '#007EB1',    # 4.2. senescence
    '#774401',    # 5. evading growth suppressors
    '#774401',    # 5.1. deregulating cc checkpoints
    '#774401',    # 5.1.1. deregulating--cell cycle
    '#774401',    # 5.2 evading contact inhibition
    '#1D3B96',    # 6. genome instability and mutation
    '#1D3B96',    # 6.1. DNA damage
    '#1D3B96',    # 6.1.1. DNA adducts
    '#1D3B96',    # 6.1.2. DNA strand breaks
    '#1D3B96',    # 6.2. DNA repair
    '#1D3B96',    # 6.3. mutation
    '#F03B34',    # 7. inducing angiogenesis
    '#F03B34',    # 7.1. deregulating angiogenesis
    '#F03B34',    # 7.1.1. angiogenic factors
    '#839098',    # 8. resisting cell death
    '#839098',    # 8.1. apoptosis
    '#839098',    # 8.2. autophagy
    '#839098',    # 8.3. necrosis
    '#019E5A',    # 9. sustaining proliferative signaling
    '#019E5A',    # 9.1. proliferative signaling--cell cycle
    '#019E5A',    # 9.2. growth signals
    '#019E5A',    # 9.2.1. growth signals--downstream signaling
    '#019E5A',    # 9.3. proliferative signaling--receptors
    '#E17A1C',    # x. tumor promoting inflammation
    '#E17A1C',    # x.1. immune response
    '#E17A1C',    # x.2. inflammation
    '#E17A1C',    # x.2.1. oxidative stress
]
