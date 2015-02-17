import sys, os
sys.path.append("./code/")
from status_reader import get_statuses
import argparse

parser = argparse.ArgumentParser(description="Run Topic Model test")
parser.add_argument('-ne_pp', action='store_true', help="re-run preprocessing of neuro data")
parser.add_argument('-tw_pp', action='store_true', help="re-run preprocessing of twitter data")
parser.add_argument('-ne_pp_tag', default = "")
parser.add_argument('-tw_pp_tag', default = "")
parser.add_argument('-ne', default="", help="neuro dataset experiment")
parser.add_argument('-tw', default="", help="twitter dataset experiment")
parser.add_argument('-ne_run', action='store_true', help="re-run preprocessing of neuro data")
parser.add_argument('-tw_run', action='store_true', help="re-run preprocessing of twitter data")
parser.add_argument('-prior', action='store_true')
parser.add_argument('-predict', action='store_true')
parser.add_argument('-pos_file', default="depressed")
parser.add_argument('-neg_file', default="control")
parser.add_argument('-in_tag', default="dev")
parser.add_argument('-out_tag', default="")
parser.add_argument('-model_dir', default="")
parser.add_argument('--k', default="50", help="number of topics")
parser.add_argument('--b', help="include bigrams", action='store_const', const=5, default=5000)
parser.add_argument('--l', action='store_true', help="perform lemmitization")
parser.add_argument('--ni', default='500', help="number of iterations")
parser.add_argument('--bi', default='100', help="number of burn-in iterations")
parser.add_argument('--u', help="limit unigrams", action='store_const', const=50, default=1)
parser.add_argument('--V', help="limit vocab to 10000", action='store_true')
parser.add_argument('-vocab', default="")
args = parser.parse_args()


MALLET="/home/will/Research/CLPsych/external/mallet-2.0.7/bin/mallet"
#MALLET=external/Mallet/bin/mallet
BASENAME1=args.pos_file
BASENAME2=args.neg_file
TAG_I=args.in_tag
TAG_O=args.out_tag
BASENAME=BASENAME1+"_x_"+BASENAME2
NUM_TOPS=args.k
SEED=0

JAVA = "java -Xmx10000M -cp 'segan/dist/segan.jar:segan/lib/*'"
BASEDIR="/home/will/Final"

import datetime
cur_time = datetime.datetime.now()
if args.model_dir == "":
        out_dir = "output/exp/" + TAG_O + "_" + datetime.datetime.isoformat(cur_time)
else:
        out_dir = args.model_dir
if not os.path.exists(out_dir):
        os.system("mkdir "+out_dir)

args_file = open(out_dir+"/args.txt", "w")
args_file.write(str(args))
args_file.close()

log_file = open(out_dir + "/log.txt", "a")

class_map_pp = {'lda':'data.TextDataset', 'slda':'data.ResponseTextDataset', 'snlda':'data.ResponseTextDataset', 'bslda':'data.LabelTextDataset', 'bsnlda':'data.LabelTextDataset'}
dataset="neuro-data"
folder = "neuro"
ne_in_folder = "format-" + args.ne + ("_" + args.ne_pp_tag if args.ne_pp_tag != "" else "")
if args.ne_pp:
	print "==>Preparing neuroticism data"
        class_to_run=class_map_pp[args.ne]
        cmd = [JAVA,
               class_to_run,
               "--dataset " + dataset,
               "--data-folder segan/" + folder, 
               "--text-data "+BASEDIR+"/input/raw/neuro",
               "--format-folder " + ne_in_folder,
               "--run-mode process",
               "-v -d -s -sent",
               "--u " + str(args.u),
               "--bs " + str(args.b * 2),
               "--b " + str(args.b)]
        if args.vocab != "":
                cmd.append("--word-voc-file " + args.vocab)
        if args.l:
                cmd.append("--l")
        if args.ne == "slda" or args.ne=="snlda":
                cmd.append("--response-file " + BASEDIR + "/input/raw/neuro_response_file.txt")
        if args.prior:
                cmd.append("--word-voc-file /home/will/Final/combined_vocab.txt")
        if args.V:
                cmd.append("--V 10000")
        log_file.write(" ".join(cmd) + "\n\n")
        os.system(" ".join(cmd))


NUM_ITER=args.ni
NUM_BI=args.bi
alpha =str(1)

class_map = {'lda':"sampler.unsupervised.LDA", 
             "slda" : "sampler.supervised.regression.SLDA",
             "snlda" : "sampler.supervised.regression.SNLDA",
             "bsnlda" : "sampler.supervised.regression.SNLDA"}
args_map = {'lda':["--K "+NUM_TOPS, "--alpha " + alpha,  "--beta 0.01"]}
args_map["slda"] = args_map["lda"] + ["--rho 1.0 --sigma 1.0 --mu 0.0 -z --train"]
args_map["snlda"] = ["--Ks " + NUM_TOPS,
                     "--alphas "+alpha+","+alpha,
                     "--betas 0.25,0.1,0.05",
                     "--gamma-means 0.2,0.2 --gamma-scales 100,10",
                     "--rho 0.1 --mu 0.0 --sigma 1.0 -z"]
args_map["bsnlda"] = args_map["snlda"] + ["-binary"]
if args.ne_run:
	print "==>Training lda on neuroticism data"
        class_to_run = class_map[args.ne]
        file_prefix = "segan/"+folder+"/"+dataset+"/"+ne_in_folder+"/"+dataset
	cmd = [JAVA,
               class_to_run,
               "--dataset " + dataset,
               "--word-voc-file "+file_prefix+".wvoc",
               "--word-file "+file_prefix+".dat",
               "--info-file "+file_prefix+".docinfo",
               "--output-folder "+out_dir+"/"+dataset+"/models",
               "--burnIn "+NUM_BI,
               "--maxIter "+NUM_ITER,
               "--sampleLag 25 --report 5 --init random -v -d",
           ]
        cmd += args_map[args.ne]

        log_file.write(" ".join(cmd) + "\n\n")
        os.system(" ".join(cmd))
        

if not os.path.exists("input/" + TAG_I):
	os.system("mkdir input/" + TAG_I)

if not os.path.exists("input/"+TAG_I+"/"+BASENAME+"_text.csv"):
	print "==>Processing Raw Data"
	os.system("mkdir input/"+TAG_I+"/"+BASENAME)
	get_statuses("input/raw/"+BASENAME1, "input/"+TAG_I+"/"+BASENAME, 1, "input/raw/dev_set.txt")
        get_statuses("input/raw/"+BASENAME2, "input/"+TAG_I+"/"+BASENAME, 0, "input/raw/dev_set.txt")

folder = "twitter"
dataset = TAG_I
tw_in_folder = "format-" + args.tw + ("_" + args.tw_pp_tag if args.tw_pp_tag != "" else "")
if args.tw_pp:
	print "==>Prepping twitter input file"
        class_to_run=class_map_pp[args.tw]
        cmd = [JAVA,
               class_to_run,
               "--dataset " + dataset,
               "--data-folder segan/" + folder,                
               #"--text-data "+BASEDIR+"/input/"+TAG_I+"/"+BASENAME+"_text.csv",
               "--text-data "+BASEDIR+"/input/raw/control_depression/controldepression.users.train.text",
               "--format-folder " + tw_in_folder,
               "--run-mode process",
               "-v -d -s -sent",
               "--u " + str(args.u),
               "--bs " + str(args.b * 2),
               "--b " + str(args.b)]
        if args.vocab != "":
                cmd.append("--word-voc-file " + args.vocab)
        if args.l:
                cmd.append("--l")
        if args.tw == "slda" or args.tw=="snlda":
                cmd.append("--response-file " + BASEDIR + "/input/"+TAG_I+"/"+BASENAME+"_label.csv")
        if args.tw == "bslda" or args.tw=="bsnlda":
                #cmd.append("--label-file " + BASEDIR + "/input/"+TAG_I+"/"+BASENAME+"_label.csv")
                cmd.append("--label-file " + BASEDIR + "/input/raw/control_depression/controldepression.users.train.label")
        if args.prior:
                cmd.append("--word-voc-file segan/neuro/neuro-data/"+ne_in_folder+"/neuro-data.wvoc")
        if args.V:
                cmd.append("--V 10000")
        log_file.write(" ".join(cmd) + "\n\n")
        os.system(" ".join(cmd))

if args.ne == 'lda':
        NEURO_DIR=out_dir+"/neuro-data/models/RANDOM_LDA_K-"+NUM_TOPS+"_B-"+NUM_BI+"_M-"+NUM_ITER+"_L-25_a-"+alpha+"_b-0.01_opt-false"
elif args.ne == 'slda':
	NEURO_DIR=out_dir+"/neuro-data/models/RANDOM_SLDA_K-"+NUM_TOPS+"_B-"+NUM_BI+"_M-"+NUM_ITER+"_L-25_a-"+alpha+"_b-0.01_r-1_m-0_s-1_opt-false"
#NUM_ITER=100
#NUM_BI=`expr $NUM_ITER / 5`

if args.tw_run:
	print "==>Infering topics with " + args.tw
        class_to_run = class_map[args.tw]
        file_prefix = "segan/"+folder+"/"+dataset+"/"+tw_in_folder+"/"+dataset
        cmd = [JAVA,
               class_to_run,
               "--dataset " + dataset,
               "--word-voc-file "+file_prefix+".wvoc",
               "--word-file "+file_prefix+".dat",
               "--info-file "+file_prefix+".docinfo",
               "--output-folder "+out_dir+"/twitter/"+TAG_I+"/models",
               "--burnIn "+NUM_BI,
               "--maxIter "+NUM_ITER,
               "--sampleLag 25 --report 5 --init random -v -d"
           ]
        if args.prior:
                cmd.append("--prior-topic-file "+NEURO_DIR+"/posterior.csv")
        cmd += args_map[args.tw]

        log_file.write(" ".join(cmd) + "\n\n")
        os.system(" ".join(cmd))


if not args.predict:
        exit()

print "==>Converting to CSV"
os.system("mkdir " + out_dir + "/slda-tops_"+NUM_ITER)

def run_cmd(c):
        log_file.write(c)
        os.system(c)

if args.tw == 'lda' or args.tw == '':
        TW_DIR=out_dir+"/twitter/"+TAG_I+"/models/RANDOM_LDA_K-"+NUM_TOPS+"_B-"+NUM_BI+"_M-"+NUM_ITER+"_L-25_a-"+alpha+"_b-0.01_opt-false"
elif args.tw == 'slda':
	TW_DIR=out_dir+"/twitter/"+TAG_I+"/models/RANDOM_SLDA_K-"+NUM_TOPS+"_B-"+NUM_BI+"_M-"+NUM_ITER+"_L-25_a-"+alpha+"_b-0.01_r-1_m-0_s-1_opt-false"
	
run_cmd("unzip "+TW_DIR+"/report/iter-"+NUM_ITER+".zip")

run_cmd("python code/get_topics.py iter-"+NUM_ITER+".assignment segan/twitter/"+TAG_I+"/"+tw_in_folder+"/"+TAG_I+".docinfo "+out_dir+"/slda-tops_"+NUM_ITER+" SLDA-"+NUM_TOPS+"-"+TAG_O)
	
run_cmd("python code/extract_to_csv.py "+out_dir+"/slda-tops_"+NUM_ITER+" "+out_dir + "/slda-tops_"+NUM_ITER+".csv")

run_cmd("rm iter-"+NUM_ITER+".*")


run_cmd('java -Xmx10000M -cp /usr/share/java/weka.jar weka.classifiers.meta.FilteredClassifier -F "weka.filters.unsupervised.attribute.Remove -R 1" -W weka.classifiers.bayes.NaiveBayes -i -k -t '+out_dir+'/slda-tops_'+NUM_ITER+'.csv >> '+log_file.name)
#java -Xmx10000M -cp /usr/share/java/weka.jar weka.classifiers.bayes.BayesNet  -i -k -t output/$TAG/$BASENAME-infered.csv -D -Q weka.classifiers.bayes.net.search.local.K2 -- -P 1 -S BAYES -E weka.classifiers.bayes.net.estimate.SimpleEstimator -- -A 0.5



