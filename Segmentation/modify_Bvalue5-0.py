import argparse
import numpy as np
# python /home/haolin/Research/Segmentation/modify_Bvalue5-0.py --inbval input.bval --inbvec input.bvec --outbval output.bval --outbvec output.bvec

def modify_bvalue_and_bvec(in_bval_path, in_bvec_path, out_bval_path, out_bvec_path):
    # Load b-values and b-vectors
    bval = np.loadtxt(in_bval_path)
    bvec = np.loadtxt(in_bvec_path)

    # Find rows with b-value equal to 5.0 and set them to 0
    rows_to_modify = np.where(bval == 5.0)[0]
    if len(rows_to_modify) > 0:
        print(f"Found {len(rows_to_modify)} rows with b-value equal to 5.0. Modifying...")
        bval[rows_to_modify] = 0.0
        bvec[:, rows_to_modify] = 0.0
    else:
        print("No rows with b-value equal to 5.0 found. No modifications needed.")

    # Save modified b-values and b-vectors
    np.savetxt(out_bval_path, bval, fmt='%.7e')
    np.savetxt(out_bvec_path, bvec, fmt='%.7e')

    print("Modified b-values and b-vectors saved to output files.")

def main():
    parser = argparse.ArgumentParser(description="Modify b-values and corresponding b-vectors.")
    parser.add_argument("--inbval", required=True, help="Path to the input bval file.")
    parser.add_argument("--inbvec", required=True, help="Path to the input bvec file.")
    parser.add_argument("--outbval", required=True, help="Path to the output modified bval file.")
    parser.add_argument("--outbvec", required=True, help="Path to the output modified bvec file.")
    args = parser.parse_args()

    modify_bvalue_and_bvec(args.inbval, args.inbvec, args.outbval, args.outbvec)

if __name__ == "__main__":
    main()


