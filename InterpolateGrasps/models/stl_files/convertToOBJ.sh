for file in *.STL; do
    meshlabserver -i "$file" -o "${file%.*}.obj" # -om vc
done
