import sys
import argparse
import urllib2
import shutil

##### parse arguments
parser = argparse.ArgumentParser(description="Converters a .vcf file to a .bed file.");
parser.add_argument('-i', '--input', required=True, help="The name of the input file containing a list of TCGA ids. Each id can be quoted or unquoted. Only the first 12 characters of each id will be used.");
parser.add_argument('-t', '--type', required=True, choices=['mRNA','miRNA','both'], help="Type of data to export. Option 'both' specifies both mRNA AND miRNA.");
parser.add_argument('-q', '--query', required=False, action='store_true', help="If this option is included, a TCGA QUERY will be outputed to stdout and a manifest will not be downloaded.");
parser.add_argument('-m', '--manifest', required=False, help="The name of the file to download the manifest to (will overwrite file if it already exists). If this argument is not specified (and neither is -q), manifest will be outputed to stdout");
parser.add_argument('-d', '--metadata', required=False, help="The name of the file to download the JSON metadata to (will overwrite file if it already exists). If this argument is not specified (and neither is -q), metadata will be outputed to stdout");

_args = parser.parse_args();
globals()['args'] = _args;
#####

##### ___main___ #####

if args.input == args.manifest or args.input == args.metadata:
    print("Input and output cannot be the same file")
    sys.exit()

input_file = open(args.input);
list = ""
for line in input_file:
    list += ('"' + line.strip('"').strip() + '"') + ",";
list = list[:-1]

if args.type == "mRNA":
    types = '"*.htseq.counts*", "*.FPKM.txt*", "*.FPKM-UQ.txt*"';
elif args.type == "miRNA":
    types = '"*.isoforms.quantification.txt*"'
else:
    types = '"*.htseq.counts*", "*.FPKM.txt*", "*.FPKM-UQ.txt*", "*.isoforms.quantification.txt*"';

if args.query == True:
    print('files.file_name in [' + types + '] and cases.project.program.name in ["TCGA"] and cases.submitter_id in [' + list + ']');
else:
    fields = "md5sum,data_type,file_name,downstream_analyses.workflow_type,downstream_analyses.output_files.data_type,downstream_analyses.output_files.file_name,downstream_analyses.output_files.data_format,downstream_analyses.output_files.access,downstream_analyses.output_files.file_id,downstream_analyses.output_files.data_category,downstream_analyses.output_files.file_size,file_size,data_format,analysis.analysis_id,analysis.updated_datetime,analysis.created_datetime,analysis.submitter_id,analysis.state,analysis.workflow_link,analysis.workflow_type,analysis.workflow_version,submitter_id,access,platform,state,file_id,data_category,associated_entities.entity_id,associated_entities.case_id,associated_entities.entity_submitter_id,associated_entities.entity_type,experimental_strategy"
    if args.manifest != None:
        manifest_stream = open(args.manifest, "wb");
    else:
        manifest_stream = sys.stdout
    if args.metadata != None:
        metadata_stream = open(args.metadata, "wb");
    else:
        metadata_stream = sys.stdout
    post = '{"filters":{"op":"and","content":[{"op":"in","content":{"field":"files.file_name","value":[' + types + ']}},{"op":"in","content":{"field":"cases.project.program.name","value":["TCGA"]}},{"op":"in","content":{"field":"cases.submitter_id","value":[' + list + ']}}]},"size":"99999999","fields":"' + fields + '"}';
    r = urllib2.Request("https://api.gdc.cancer.gov/files?return_type=manifest", data=post)
    r.add_header("Content-Type",'application/json')
    u = urllib2.urlopen(r)
    shutil.copyfileobj(u, manifest_stream)

    r_meta = urllib2.Request("https://api.gdc.cancer.gov/files", data=post)
    r_meta.add_header("Content-Type",'application/json')
    u_meta = urllib2.urlopen(r_meta)
    shutil.copyfileobj(u_meta, metadata_stream)

#for line in vcf_file:
#    firstTabIndex = line.index('\t');
#    secondTabIndex = line.index('\t', firstTabIndex + 1);
#    pos = int(line[firstTabIndex:secondTabIndex]);
#    bed_stream.write('\t'.join(["chr" + line[0:firstTabIndex], str(pos - 1), str(pos), line[secondTabIndex + 1:]]));

#########################
