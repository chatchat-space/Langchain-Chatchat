
cd ./service
nohup pnpm start > service.log &
echo "Start service complete!"


cd ..
echo "" > front.log
nohup pnpm dev > front.log &
echo "Start front complete!"
tail -f front.log
