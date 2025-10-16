#dot -Tpng soft_open_arch1.dot -o ./result/soft_open_arch1.png
#dot -Tpng ./parts/definition.dot -o ./result/definition.png
#dot -Tpng ./parts/face_overview.dot -o ./result/face_overview.png
#dot -Tpng ./parts/MOSA_law.dot -o ./result/MOSA_law.png
#dot -Tpng ./parts/DOD.dot -o ./result/DOD.png
dot -Tpng ./parts/soa_feature_benifits.dot -o ./result/soa_feature_benifits.png
#eog ./result/soft_open_arch1.png
#eog ./result/DOD.png
eog ./result/soa_feature_benifits.png
#eog ./result/definition.png
git add . && git commit -m "x" && git push origin main:main
