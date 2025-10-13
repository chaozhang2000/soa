dot -Tpng soft_open_arch1.dot -o soft_open_arch1.png
dot -Tpng definition.dot -o definition.png
dot -Tpng face_overview.dot -o face_overview.png
#eog soft_open_arch1.png
git add . && git commit -m "x" && git push origin main:main
