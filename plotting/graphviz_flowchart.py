import pygraphviz as pgv

g = pgv.AGraph("""
digraph {
rankdir=LR;
ranksep=0.2;
nodesep=.5;


    start [
        label="Load\nSequence",
        fontcolor=black,
        color="#ff7f0e",
        shape=box,        
    ];
    
    slice [
        label="Slice\nSequence",
        fontcolor=black,
        color="#1f77b4",
        shape=box,        
    ];
    
    saveNom [
        label="Save\nNominal",
        fontcolor="#1f77b4",
        color="#1f77b4",
        shape=oval,
    ];
    
    match [
        label="Match\nTunes",
        fontcolor=black,
        color="#1f77b4",
        shape=box,        
    ];
    
    outNominal [
        label="PTC Output\n'Nominal'",
        fontcolor=white,
        color="#1f77b4",
        style=filled,
        shape=oval,
        fillcolor="#2f97d4",   
    ];
    
    errors [
        label="Load\nWISE Errors",
        fontcolor=black,
        color="#ff7f0e",
        shape=box,        
    ];    
    
    applyMQX [
        label="Apply\nMQX Errors",
        fontcolor=black,
        color="#1f77b4",
        shape=box,        
    ];
    
    outMQX [
        label="PTC Output\n'Only MQX'",
        fontcolor=white,
        color="#1f77b4",
        style=filled,
        shape=oval,
        fillcolor="#2f97d4",   
    ];
    
    applyAll [
        label="Apply all\nother IP Errors",
        fontcolor=black,
        color="#1f77b4",
        shape=box,        
    ];
    
    outAll [
        label="PTC Output\n'All Errors'",
        fontcolor=white,
        color="#1f77b4",
        style=filled,
        shape=oval,
        fillcolor="#2f97d4",   
    ];
    
    calcCorrection [
        label="Calculate\nCorrections",
        fontcolor=black,
        color="#1f77b4",
        shape=box,        
    ];
    
    loadCorrection [
        label="Load\nCorrections",
        fontcolor=black,
        color="#ff7f0e",
        shape=box,        
    ];    
    
    outApplied [
        label="PTC Output\n'Corrected'",
        fontcolor=white,
        color="#1f77b4",
        style=filled,
        shape=oval,
        fillcolor="#2f97d4",   
    ];
    
    saveCorrection [
        label="Save\nCorrections",
        fontcolor="#1f77b4",
        color="#1f77b4",
        shape=oval,
    ];
    
    outLoaded [
        label="PTC Output\n'Corrected by ...'",
        fontcolor=white,
        color="#1f77b4",
        style=filled,
        shape=oval,
        fillcolor="#2f97d4",   
    ];
       
    

ordering=out;    
{rank=same; outNominal; match;}
{rank=same; outMQX; applyMQX;}
{rank=same; outAll; applyAll;}
{rank=same; outApplied; outLoaded;}
{rank=same; saveNom; slice;}
{rank=same; calcCorrection; loadCorrection; saveCorrection;}



match -> outNominal;
applyMQX -> outMQX;
applyAll -> outAll;

start -> slice -> match -> errors -> applyMQX -> applyAll -> calcCorrection -> outApplied;

slice -> saveNom;
saveNom -> calcCorrection [style=dashed];
applyAll -> loadCorrection; 
calcCorrection -> saveCorrection [style=dashed];
loadCorrection -> outLoaded [label="e.g. other beam,\n30/30"];
saveCorrection -> loadCorrection [style=dashed];
edge[style=invis];
outNominal -> outMQX -> outAll -> loadCorrection;


}
""")


g.layout(prog='dot')
g.draw("/media/jdilly/Storage/Notebooks/phd_prelim_rdt_comparison/images/flowchart.png")
