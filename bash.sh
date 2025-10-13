dot -Tpng soft_open_arch1.dot -o ./result/soft_open_arch1.png
dot -Tpng ./parts/definition.dot -o ./result/definition.png
dot -Tpng ./parts/face_overview.dot -o ./result/face_overview.png
eog ./result/soft_open_arch1.png
#git add . && git commit -m "x" && git push origin main:main
