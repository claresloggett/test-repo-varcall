stageDefaults = {
    'distributed': True,
    'walltime': "08:00:00",
    'memInGB': 8,
    'queue': "batch",
    'modules': [
        "bwa-gcc/0.5.9",
        "samtools-gcc/0.1.16",
        "picard/1.53",
        "python-gcc/2.6.4",
        "R-gcc/2.12.0",
        "gatk/1.6-7"
    ]
}
stages = {
    "fastqc": {
        "command": "fastqc --quiet -o %outdir %seq",
        "walltime": "10:00:00",
        'modules': [ "fastqc/0.10.1" ]
    },
    'alignBWA': {
        'command': "bwa aln -t 8 %encodingflag %ref %seq > %out",
        'walltime': "18:00:00",
        'queue': 'smp',
        'memInGB': 23
    },
    'alignToSamSE': {
        'command': "bwa samse %ref %meta %align %seq > %out"
    },
    'alignToSamPE': {
        'command': "bwa sampe %ref %meta %align1 %align2 %seq1 %seq2 > %out"
    },
    'samToSortedBam': {
        'command': "./SortSam 6 VALIDATION_STRINGENCY=LENIENT INPUT=%seq OUTPUT=%out SORT_ORDER=coordinate",
        'walltime': "32:00:00",
    },
    'mergeBams': {
        'command': "./PicardMerge 6 %baminputs USE_THREADING=true VALIDATION_STRINGENCY=LENIENT AS=true OUTPUT=%out",
        'walltime': "72:00:00"
    },
    'indexBam': {
        'command': "samtools index %bam"
    },
    'flagstat': {
        'command': "samtools flagstat %bam > %out",
        'walltime': "00:10:00"
    },
    'igvcount': {
        'command': "igvtools count %bam %out hg19",
        'modules': [ "igvtools/1.5.15" ]
    },
    'indexVCF': {
        'command': "./vcftools_prepare.sh %vcf",
        'modules': [ "tabix/0.2.5" ]
    },
    'realignIntervals': {
        # Hard-coded to take 2 known indels files right now
        'command': "./GenomeAnalysisTK 1 -T RealignerTargetCreator -R %ref -I %bam --known %indels_goldstandard --known %indels_1000G -log %log -o %out",
        'memInGB': 23,
        'walltime': "7:00:00:00"
    },
    'realign': {
        'command': "./GenomeAnalysisTK 22 -T IndelRealigner -R %ref -I %bam -targetIntervals %intervals -log %log -o %out",
        'memInGB': 23,
        'walltime': "7:00:00:00"
    },
    'dedup': {
        'command': "./MarkDuplicates 6 INPUT=%bam REMOVE_DUPLICATES=true VALIDATION_STRINGENCY=LENIENT AS=true METRICS_FILE=%log OUTPUT=%out",
        'walltime': '7:00:00:00'
    },
    'baseQualRecalCount': {
        'command': "./GenomeAnalysisTK 12 -T CountCovariates -I %bam -R %ref --knownSites %dbsnp -nt 8 -l INFO -cov ReadGroupCovariate -cov QualityScoreCovariate -cov CycleCovariate -cov DinucCovariate -log %log -recalFile %out",
        'queue': 'smp',
        'memInGB': 23,
        'walltime': "3:00:00:00"
    },
    'baseQualRecalTabulate': {
        'command': "./GenomeAnalysisTK 4 -T TableRecalibration -I %bam -R %ref -recalFile %csvfile -l INFO -log %log -o %out",
        'walltime': "3:00:00:00"
    },
    'callSNPs': {
        'command': "./GenomeAnalysisTK 12 -T UnifiedGenotyper -nt 8 -R %ref -I %bam --dbsnp %dbsnp -stand_call_conf 50.0 -stand_emit_conf 10.0 -dcov 1600 -l INFO -A AlleleBalance -A DepthOfCoverage -A FisherStrand -glm SNP -log %log -o %out",
        'queue': 'smp',
        'memInGB': 23,
        'walltime': "24:00:00"
    },
    'callIndels': {
        'command': "./GenomeAnalysisTK 12 -T UnifiedGenotyper -nt 8 -R %ref -I %bam --dbsnp %dbsnp -stand_call_conf 50.0 -stand_emit_conf 10.0 -dcov 1600 -l INFO -A AlleleBalance -A DepthOfCoverage -A FisherStrand -glm INDEL -log %log -o %out",
        'queue': 'smp',
        'memInGB': 23,
        'walltime': "24:00:00"
    },
    'filterSNPs': {
        # Very minimal filters based on GATK recommendations. VQSR is preferable if possible.
        'command': "./GenomeAnalysisTK 4 -T VariantFiltration -R %ref --variant %vcf --filterExpression 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || HaplotypeScore > 13.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' --filterName 'GATK_MINIMAL_FILTER' -log %log -o %out",
    },
    'filterIndels': {
        # Very minimal filters based on GATK recommendations. VQSR is preferable if possible.
        # If you have 10 or more samples GATK also recommends the filter InbreedingCoeff < -0.8
        'command': "./GenomeAnalysisTK 4 -T VariantFiltration -R %ref --variant %vcf --filterExpression 'QD < 2.0 || ReadPosRankSum < -20.0 || FS > 200.0' --filterName 'GATK_MINIMAL_FILTER' -log %log -o %out",
    },
    'annotateEnsembl': {
        # This command as written assumes that VEP and its cache have been
        # downloaded in respective locations
        # ./variant_effect_predictor_2.5
        # ./variant_effect_predictor_2.5/vep_cache
        'command': "perl variant_effect_predictor_2.5/variant_effect_predictor.pl --cache --dir variant_effect_predictor_2.5/vep_cache -i %vcf --vcf -o %out -species human --canonical --gene --protein --sift=b --polyphen=b > %log",
        'modules': [ "perl/5.10.1", "ensembl/67" ]
    },
    'depthOfCoverage': {
        'command': "./GenomeAnalysisTK 4 -T DepthOfCoverage -R %ref -I %bam -omitBaseOutput -ct 1 -ct 10 -ct 20 -ct 30 -o %out",
    },
    'collateReadcounts': {
        'command': 'python count_flagstat_wgs.py %dir %outdir',
        'walltime': "00:10:00"
    }
}
