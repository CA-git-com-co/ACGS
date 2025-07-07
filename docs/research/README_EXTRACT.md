# Research Materials Extraction Guide

Due to Git repository size constraints, the research materials are stored as compressed archives.

## Extracting Research Papers

To extract the research papers collection:

```bash
cd docs/research
tar -xzf papers_archive.tar.gz
```

This will create a `papers/` directory containing 136 research papers related to:
- Constitutional AI and alignment
- Reward modeling and RLHF
- Preference optimization techniques
- Language model safety and robustness

## Extracting arXiv Paper Images

To extract the images for the arXiv paper (arXiv-2506.16507v1):

```bash
cd docs/research/arXiv-2506.16507v1
tar -xzf images_archive.tar.gz
```

This will restore the PDF figures and charts used in the paper.

## Archive Contents

- `papers_archive.tar.gz`: Complete collection of research papers (136 PDFs)
- `arXiv-2506.16507v1/images_archive.tar.gz`: Paper figures and illustrations

## Size Information

- Papers archive: ~175MB compressed
- Images archive: ~2MB compressed
- Total extracted size: ~600MB

## Automated Extraction

You can also use the provided script:

```bash
./docs/research/extract_all.sh
```

This will extract both archives automatically.
