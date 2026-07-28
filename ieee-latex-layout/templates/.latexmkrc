# Build PDF and remove intermediate files after a successful run.
$pdf_mode = 1;
$interaction = 'nonstopmode';

$success_cmd = 'rm -f %R.aux %R.log %R.blg %R.bbl %R.fls %R.fdb_latexmk %R.out %R.synctex.gz';
