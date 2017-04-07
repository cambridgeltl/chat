_top_hallmark_legend = '''<div class="chart-legend" id="chart-legend">
  <ul class="0-legend">
    <li><span style="background-color:#221E1F"></span>invasion and metastasis</li>
    <li><span style="background-color:#D1268C"></span>immune destruction</li>
    <li><span style="background-color:#813C96"></span>cellular energetics</li>
    <li><span style="background-color:#007EB1"></span>replicative immortality</li>
    <li><span style="background-color:#774401"></span>evading growth suppressors</li>
    <li><span style="background-color:#1D3B96"></span>genome instability and mutation</li>
    <li><span style="background-color:#F03B34"></span>inducing angiogenesis</li>
    <li><span style="background-color:#839098"></span>resisting cell death</li>
    <li><span style="background-color:#019E5A"></span>sustaining proliferative signaling</li>
    <li><span style="background-color:#E17A1C"></span>tumor promoting inflammation</li>
  </ul>
</div>'''

def get_legend(hallmarks='top'):
    if hallmarks == 'top':
        return _top_hallmark_legend
    elif hallmarks == 'full':
        return None
    else:
        return None
