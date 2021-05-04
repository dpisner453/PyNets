#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:40:07 2017
Copyright (C) 2016
@author: Derek Pisner (dPys)
"""
import subprocess
import re
import os
import sys
import json
import pynets
from copy import deepcopy
from collections import OrderedDict
from argparse import ArgumentParser
from pathlib import Path
from pynets.core.cloud import get_credentials
from pynets.core.cloud import get_matching_s3_objects
from pynets.core.cloud import s3_client


def batch_submit(
    bucket,
    dataset,
    push_dir,
    modality,
    participant_label,
    session_label,
    user_atlas,
    cluster_mask,
    roi,
    ref,
    way,
    plugin,
    resources,
    working_dir,
    verbose,
    jobdir,
    credentials,
):
    """Searches through an S3 bucket, gets all subject-ids, creates json
    files for each, submits batch jobs, and returns list of job ids to query
    status upon later.

    Parameters
    __________

    bucket : str
        s3 bucket
    dataset,
    push_dir,
    modality,
    participant_label,
    session_label,
    user_atlas,
    cluster_mask,
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file
    ref : str
        File path to reference Nifti1Image to use as the target for alignment.
    way,
    plugin,
    resources,
    working_dir : str
        Path to the working directory to perform SyN and save outputs
    verbose,
    jobdir : str
        Directory of batch jobs to generate/check up on credentials

    """

    print(f"Getting list from s3://{bucket}/{dataset}/...")
    seshs = crawl_bucket(bucket, dataset, jobdir)

    for sub, ses in list(seshs.items()):
        if session_label != ["None"] and session_label != [None]:
            seshs[sub] = [i for i in seshs[sub] if i in session_label]
        if participant_label != ["None"] and participant_label != [None]:
            if sub not in participant_label:
                del seshs[sub]

    jobs = create_json(
        bucket,
        dataset,
        push_dir,
        modality,
        seshs,
        user_atlas,
        cluster_mask,
        roi,
        ref,
        way,
        plugin,
        resources,
        working_dir,
        verbose,
        jobdir,
        credentials,
    )

    print("Submitting jobs to the queue...")
    submit_jobs(jobs, jobdir)


def crawl_bucket(bucket, path, jobdir):
    """Gets subject list for a given s3 bucket and path
    Parameters
    ----------
    bucket : str
        s3 bucket
    path : str
        The directory where the dataset is stored on the S3 bucket
    jobdir : str
        Directory of batch jobs to generate/check up on
    Returns
    -------
    OrderedDict
        dictionary containing all subjects and sessions from the path location
    """
    from pynets.core.utils import flatten

    # if jobdir has seshs info file in it, use that instead
    sesh_path = f"{jobdir}/seshs.json"
    if os.path.isfile(sesh_path):
        print("seshs.json found -- loading bucket info from there")
        with open(sesh_path, "r") as f:
            seshs = json.load(f)
        print("Information obtained from s3.")
        return seshs

    # set up bucket crawl
    subj_pattern = r"(?<=sub-)(\w*)(?=/ses)"
    sesh_pattern = r"(?<=ses-)(\d*)"
    all_subfiles = get_matching_s3_objects(bucket, path + "/sub-")
    all_subfiles = [obj for obj in all_subfiles]
    all_subs = [re.findall(subj_pattern, obj) for obj in all_subfiles]
    subjs = list(set([i for i in flatten(all_subs)]))
    seshs = OrderedDict()

    # populate seshs
    for subj in subjs:
        prefix = f"{path}/sub-{subj}/"
        all_seshfiles = get_matching_s3_objects(bucket, prefix)
        all_seshfiles = [obj for obj in all_seshfiles]
        all_seshs = [re.findall(sesh_pattern, obj) for obj in all_seshfiles]
        sesh = list(set([i for i in flatten(all_seshs)]))

        if sesh != []:
            seshs[subj] = sesh
            print(f"{subj} added to sessions.")
        else:
            seshs[subj] = None
            print(f"{subj} not added (no sessions).")

    # print session IDs and create json cache
    print(
        (
            "Session IDs: "
            + ", ".join(
                [
                    subj + "-" + sesh if sesh is not None else subj
                    for subj in subjs
                    for sesh in seshs[subj]
                ]
            )
        )
    )
    with open(sesh_path, "w") as f:
        json.dump(seshs, f)
    print(f"{sesh_path} created.")
    print("Information obtained from s3.")
    return seshs


def create_json(
    bucket,
    dataset,
    push_dir,
    modality,
    seshs,
    user_atlas,
    cluster_mask,
    roi,
    ref,
    way,
    plugin,
    resources,
    working_dir,
    verbose,
    jobdir,
    credentials,
):
    """Creates the json files for each of the jobs"""
    from pathlib import Path

    jobsjson = f"{jobdir}/jobs.json"

    # set up infrastructure
    out = subprocess.check_output(f"mkdir -p {jobdir}", shell=True)
    out = subprocess.check_output(f"mkdir -p {jobdir}/jobs/", shell=True)
    out = subprocess.check_output(f"mkdir -p {jobdir}/ids/", shell=True)

    with open(
        "%s%s" % (str(Path(__file__).parent.parent),
                  "/config/cloud_config.json"), "r"
    ) as inf:
        # with
        # open('/Users/derekpisner/Applications/PyNets/pynets/
        # cloud_config.json')
        # as inf:
        template = json.load(inf)

    co = template["containerOverrides"]
    cmd = co["command"]
    env = co["environment"]

    # modify template
    if credentials is not None:
        env[0]["value"], env[1]["value"] = get_credentials()
    else:
        env = []
    co["environment"] = env

    # edit non-defaults
    procmem = list(eval(str(resources)))
    jobs = []
    cmd[cmd.index("<INPUT>")] = f"s3://{bucket}/{dataset}"
    cmd[cmd.index("<PUSH>")] = f"s3://{bucket}/{push_dir}"
    cmd[cmd.index("<MODALITY>")] = modality[0]
    co["vcpus"] = int(procmem[0])
    co["memory"] = int(1000 * float(procmem[1]))

    if user_atlas is not None:
        cmd.append("-ua")
        for i in user_atlas:
            cmd.append(i)
    if cluster_mask is not None:
        cmd.append("-cm")
        for i in cluster_mask:
            cmd.append(i)
    if roi is not None:
        cmd.append("-roi")
        for i in roi:
            cmd.append(i)
    if ref is not None:
        cmd.append("-ref")
        for i in ref:
            cmd.append(i)
    if way is not None:
        cmd.append("-way")
        for i in way:
            cmd.append(i)
    if verbose is True:
        cmd.append("-v")
    if plugin is not None:
        cmd.append("-plug")
        cmd.append(plugin)
    if plugin is not None:
        cmd.append("-pm")
        cmd.append(resources)
    if working_dir is not None:
        cmd.append("-work")
        cmd.append(working_dir)

    # edit participant-specific values ()
    # loop over every session of every participant
    for subj in seshs.keys():
        print(f"Generating job for sub-{subj}")
        # and for each subject number in each participant number,
        for sesh in seshs[subj]:
            # add format-specific commands,
            job_cmd = deepcopy(cmd)
            job_cmd[job_cmd.index("<SUBJ>")] = subj
            if sesh is not None:
                job_cmd[job_cmd.index("<SESH>")] = sesh

            # then, grab the template,
            # add additional parameters,
            # make the json file for this iteration,
            # and add the path to its json file to `jobs`.
            job_json = deepcopy(template)
            ver = pynets.__version__.replace(".", "-")
            if dataset:
                name = f"pynets_{ver}_{dataset}_sub-{subj}"
            else:
                name = f"pynets_{ver}_sub-{subj}"
            if sesh is not None:
                name = f"{name}_ses-{sesh}"
            print(job_cmd)
            job_json["jobName"] = name
            job_json["containerOverrides"]["command"] = job_cmd
            job = os.path.join(jobdir, "jobs", name + ".json")
            with open(job, "w") as outfile:
                json.dump(job_json, outfile)
            jobs += [job]

    # return list of job jsons
    with open(jobsjson, "w") as f:
        json.dump(jobs, f)
    return jobs


def submit_jobs(jobs, jobdir):
    """Give list of jobs to submit, submits them to AWS Batch
    Parameters
    ----------
    jobs : list
        Name of the json files for all jobs to submit
    jobdir : str
        Directory of batch jobs to generate/check up on
    Returns
    -------
    int
        0
    """

    batch = s3_client(service="batch")

    for job in jobs:
        with open(job, "r") as f:
            kwargs = json.load(f)
        print(f"Submitting Job: {job}")
        submission = batch.submit_job(**kwargs)
        print(
            (f'Job Name: {submission["jobName"]}, '
             f'Job ID: {submission["jobId"]}'))
        sub_file = os.path.join(jobdir, "ids", submission["jobName"] + ".json")
        with open(sub_file, "w") as outfile:
            json.dump(submission, outfile)
        print("Submitted.")
    return 0


def kill_jobs(jobdir, reason='"Killing job"'):
    """Given a list of jobs, kills them all
    Parameters
    ----------
    jobdir : str
        Directory of batch jobs to generate/check up on
    reason : str, optional
        Task you want to perform on the jobs, by default '"Killing job"'
    """

    print(f"Cancelling/Terminating jobs in {jobdir}/ids/...")
    jobs = os.listdir(jobdir + "/ids/")
    batch = s3_client(service="batch")
    jids = []
    names = []

    # grab info about all the jobs
    for job in jobs:
        with open(f"{jobdir}/ids/{job}", "r") as inf:
            submission = json.load(inf)
        jid = submission["jobId"]
        name = submission["jobName"]
        jids.append(jid)
        names.append(name)

    for jid in jids:
        print(f"Terminating job {jid}")
        batch.terminate_job(jobId=jid, reason=reason)


def main():
    parser = ArgumentParser(
        description="PyNets AWS Cloud CLI: A Fully-Automated Workflow for "
                    "Reproducible Ensemble Sampling of Functional and "
                    "Structural Connectomes")
    parser.add_argument("--bucket", help="""The S3 bucket name.""")
    parser.add_argument(
        "--dataset",
        help="""The directory with the input dataset formatted according to
                the BIDS standard such that `s3://<bucket>/<dataset>`
                as the input directory.""",
    )
    parser.add_argument(
        "modality",
        metavar="modality",
        nargs="+",
        choices=[
            "dwi",
            "func"],
        help="Specify data modality to process from bids directory. "
             "Options are `dwi` and `func`.",
    )
    parser.add_argument(
        "--participant_label",
        help="""The label(s) of the participant(s) that should be analyzed.
                The label corresponds to sub-<participant_label> from the
                BIDS spec (so it does not include "sub-"). If this parameter
                is not provided all subjects should be analyzed. Multiple
                participants can be specified with a space separated list.""",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--session_label",
        help="""The label(s) of the session that should be analyzed. The label
                corresponds to ses-<participant_label> from the BIDS spec
                (so it does not include "ses-"). If this parameter is not
                provided all sessions should be analyzed. Multiple sessions
                can be specified with a space separated list.""",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--push_location",
        action="store",
        help="Name of folder on s3 to push output data to, if the folder "
             "does not exist, it will be created. Format the location as "
             "`s3://<bucket>/<path>`",
        default=None,
    )

    # Secondary file inputs
    parser.add_argument(
        "-ua",
        metavar="Path to parcellation file in MNI-space",
        default=None,
        nargs="+",
        help="Optionally specify a path to a parcellation/atlas Nifti1Image "
             "file in MNI152 space. Labels should be spatially distinct "
             "across hemispheres and ordered with consecutive integers with a "
             "value of 0 as the background label. If specifying a list of "
             "paths to multiple user atlases, separate them by space.\n",
    )
    parser.add_argument(
        "-cm",
        metavar="Cluster mask",
        default=None,
        nargs="+",
        help="Optionally specify the path to a Nifti1Image mask file to "
             "constrained functional clustering. If specifying a list of "
             "paths to multiple cluster masks, separate them by space.\n",
    )
    parser.add_argument(
        "-roi",
        metavar="Path to binarized Region-of-Interest (ROI) Nifti1Image in "
                "template MNI space",
        default=None,
        nargs="+",
        help="Optionally specify a binarized ROI mask in template MNI space "
             "and retain only those nodes of a parcellation contained within "
             "that mask for connectome estimation.\n",
    )
    parser.add_argument(
        "-ref",
        metavar="Atlas reference file path",
        default=None,
        help="Specify the path to the atlas reference .txt file that "
             "maps labels to intensities corresponding to the atlas "
             "parcellation file specified with the -ua flag.\n",
    )
    parser.add_argument(
        "-way",
        metavar="Path to binarized Nifti1Image to constrain tractography",
        default=None,
        nargs="+",
        help="Optionally specify a binarized ROI mask in template MNI-space "
             "to constrain tractography in the case of "
             "dmri connectome estimation.\n",
    )

    # Debug/Runtime settings
    parser.add_argument(
        "--jobdir",
        action="store",
        help="""Local directory where the generated batch jobs will be
                        saved/run through in case of
                        batch termination or check-up.""",
    )
    parser.add_argument(
        "--credentials",
        action="store",
        help="csv formatted AWS credentials.",
        default=None,
    )
    parser.add_argument(
        "-pm",
        metavar="Cores,memory",
        default="auto",
        help="Number of cores to use, number of GB of memory to use for single"
             "subject run, entered as two integers seperated by comma. "
             "Otherwise, default is `auto`, which uses all resources detected "
             "on the current compute node.\n",
    )
    parser.add_argument(
        "-plug",
        metavar="Scheduler type",
        default="MultiProc",
        nargs=1,
        choices=[
            "Linear",
            "MultiProc",
            "SGE",
            "PBS",
            "SLURM",
            "SGEgraph",
            "SLURMgraph",
            "LegacyMultiProc",
        ],
        help="Include this flag to specify a workflow plugin other than the "
             "default MultiProc.\n",
    )
    parser.add_argument(
        "-v",
        default=False,
        action="store_true",
        help="Verbose print for debugging.\n")
    parser.add_argument(
        "-work",
        metavar="Working directory",
        default="/tmp/work",
        help="Specify the path to a working directory for pynets to run. "
             "Default is /tmp/work.\n",
    )

    result = parser.parse_args()

    bucket = result.bucket
    dataset = result.dataset
    push_dir = result.push_location
    modality = result.modality
    jobdir = result.jobdir
    resources = result.pm
    plugin = result.plug
    creds = result.credentials
    participant_label = result.participant_label
    session_label = result.session_label
    verbose = result.v
    working_dir = result.work
    user_atlas = result.ua
    cluster_mask = result.cm
    roi = result.roi
    ref = result.ref
    way = result.way

    if jobdir is None:
        jobdir = "./"

    print("Beginning batch submission process...")
    if not os.path.exists(jobdir):
        print("job directory not found. Creating...")
        Path(jobdir).mkdir(parents=True)

    batch_submit(
        bucket=bucket,
        dataset=dataset,
        push_dir=push_dir,
        modality=modality,
        participant_label=participant_label,
        session_label=session_label,
        user_atlas=user_atlas,
        cluster_mask=cluster_mask,
        roi=roi,
        ref=ref,
        way=way,
        plugin=plugin,
        resources=resources,
        working_dir=working_dir,
        verbose=verbose,
        jobdir=jobdir,
        credentials=creds,
    )
    sys.exit(0)


if __name__ == "__main__":
    import warnings

    warnings.filterwarnings("ignore")
    __spec__ = "ModuleSpec(name='builtins', " \
               "loader=<class '_frozen_importlib.BuiltinImporter'>)"
    main()
