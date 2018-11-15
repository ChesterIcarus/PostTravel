from output_reader import OutputLinkFlow
from network_agg import Network

# net = Network('../../data/raw/network_merged_cl.xml')
# print([link.link_id for link in list(net.links.values())[0:50]])

example = OutputLinkFlow()
network_flow = example.flow('../../data/raw/network_merged_cl.xml',
                            '../../data/raw/santiago_plans.xml')

network_flow.to_csv('../../data/processed/sample_flow.csv')
