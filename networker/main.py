import numpy as np
from networker import console, diamond, io, network, parser

def calculate_threshold(database):
    number_of_queries = database['query'].nunique()
    reccommended_cut_off = len(database.index) - (number_of_queries*3)
    database_size = len(database.index)
    counts, bins = np.histogram(database.loc[:, "identity"], bins=database_size)
    for i in np.cumsum(counts):
        if  i > reccommended_cut_off:
            threshold = bins[i]
            break
    console.print_to_system("Recommended threshold calculated at " + str(threshold) + "% identity")
    return threshold

def generate_network(database,filename):
    console.print_to_system("Generating network...")
    protein_network = network.get_new_network()
    sources = database['query']
    targets = database['subject']
    weights = database['identity']
    protein_network = network.plot_network(protein_network, sources,targets,weights)
    protein_network = network.annotate_network(protein_network)
    protein_network.show(filename)

def remove_data_under_threshold(database, threshold):
    console.print_to_system("Removing all hits below " + str(threshold) + "% identity...")
    below_threshold = []
    for i in database.index:
        identity = float(database['identity'][i])
        if identity < threshold:
            below_threshold.append(i)
    size_before = len(database.index)
    database = database.drop(below_threshold)
    size_after = len(database.index)
    console.print_to_system(str(size_before - size_after) + " hits below the threshold and have been removed!")
    return database

def parse_args():
    arg_parser = parser.get_parser()
    args = arg_parser.parse_args()
    return args

def remove_self_hits(database):
    console.print_to_system("Removing self hits...")
    self_hits = []
    for i in database.index:
        query = database['query'][i]
        subject = database['subject'][i]
        if query == subject:
            self_hits.append(i)
    size_before = len(database.index)
    database = database.drop(self_hits)
    size_after = len(database.index)
    self_hits_count = str(size_before - size_after)
    return database

def run_diamond(filename):
    diamond.make_diamond_database(filename)
    diamond.run_diamond_search(filename)
    
def main():
    console.print_to_system("Running Networker version 0.1.0")
    
    args = parse_args() 
    
    if args.tsv is None:
        if args.faa is None:
            console.print_to_system('No TSV or FAA provided; exiting')
            exit()
        console.print_to_system('No TSV provided; runing DIAMOND')
        run_diamond(args.faa)
        args.tsv = args.faa.split('.')[0] + '.tsv'
    
    database = io.read_tsv(args.tsv)

    database = remove_self_hits(database)

    if args.threshold is None:
        console.print_to_system('No threshold provided; calculating custom threshold.')
        threshold = calculate_threshold(database)
    else:
        threshold = args.threshold

    database = remove_data_under_threshold(database, threshold)

    network_filename = args.tsv.split('.')[0] + '.html'
    generate_network(database, network_filename)




