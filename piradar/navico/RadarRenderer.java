package at.innoc.roboat.radar;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.awt.image.WritableRaster;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.stage.Stage;

public class RadarRenderer extends Application implements Runnable {
    private BlockingQueue<RadarData> radarDataQueue = new LinkedBlockingQueue<>();
    private WritableRaster raster;
    private int imgw = 1024;
    private int imgh = 1024;
    private int midx, midy;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Radar Display");

        Group root = new Group();
        Canvas canvas = new Canvas(800, 800);
        GraphicsContext gc = canvas.getGraphicsContext2D();
        root.getChildren().add(canvas);
        primaryStage.setScene(new Scene(root));
        primaryStage.show();

        BufferedImage img = new BufferedImage(imgw, imgh, BufferedImage.TYPE_INT_RGB);
        raster = img.getRaster();
        midx = imgw / 2;
        midy = imgh / 2;

        new Thread(this).start(); // Start the socket server thread

        new AnimationTimer() {
            @Override
            public void handle(long now) {
                gc.clearRect(0, 0, canvas.getWidth(), canvas.getHeight());
                drawRadar(gc);
            }
        }.start();
    }

    private void drawRadar(GraphicsContext gc) {
        while (!radarDataQueue.isEmpty()) {
            RadarData data = radarDataQueue.poll();
            if (data != null) {
                double x = data.getDistance() * Math.cos(Math.toRadians(data.getAngle()));
                double y = data.getDistance() * Math.sin(Math.toRadians(data.getAngle()));
                gc.setFill(Color.hsb(data.getIntensity(), 1.0, 1.0));
                gc.fillOval(400 + x, 400 - y, 2, 2);
            }
        }
    }

    @Override
    public void run() {
        try (ServerSocket serverSocket = new ServerSocket(5000)) {
            System.out.println("Server started, waiting for connections...");
            while (true) {
                Socket socket = serverSocket.accept();
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String line;
                while ((line = in.readLine()) != null) {
                    String[] parts = line.split(",");
                    double intensity = Double.parseDouble(parts[0]);
                    double angle = Double.parseDouble(parts[1]);
                    double distance = Double.parseDouble(parts[2]);
                    radarDataQueue.add(new RadarData(intensity, angle, distance));
                }
                socket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    static class RadarData {
        private final double intensity;
        private final double angle;
        private final double distance;

        public RadarData(double intensity, double angle, double distance) {
            this.intensity = intensity;
            this.angle = angle;
            this.distance = distance;
        }

        public double getIntensity() {
            return intensity;
        }

        public double getAngle() {
            return angle;
        }

        public double getDistance() {
            return distance;
        }
    }
}