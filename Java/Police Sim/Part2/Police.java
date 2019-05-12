package Part2;

import java.util.ArrayList;
import java.awt.Point;

public class Police implements Runnable {
	private Point location;
	private String id;
	private String status;
	private Boolean dog;
	private int suspectID;
	private ArrayList<Suspects> suspects;
	private Kennel k1;
	private Suspects crim;
	private int sceneCount = 4; //second to wait at scene
	private boolean returningDog = false;
	private PoliceStation station;
	private ArrayList<PoliceStation> stations;
	private Point destination;
	
	public Police (String id, int x, int y, String status, Boolean dog, ArrayList<Suspects> suspects) {
		this.id = id;
		this.location = new Point(x, y);
		this.status = status;
		this.dog = dog;
		this.suspects = suspects;
	}
	
	public void setKennel(Kennel k) {
		this.k1 = k;
	}
	
	public void setStations(ArrayList<PoliceStation> stations) {
		this.stations = stations;
	}
	
	public Point getLocation() {
        return this.location;
    }
	
	public String getID() {
		return this.id;
	}
	
	public String getStatus() {
		return this.status;
	}
	
	public boolean getDog() {
		return this.dog;
	}
	
	public int getSuspectId() {
		return this.suspectID;
	}
	
	public String returnStatus() {
		String dogOut = (this.dog) ? "Yes" : "No"; //change dog from boolean back to yes/no
		if (this.suspectID == 0) { //No suspect assigned
			return this.id + "," + (int) this.location.getX() + "," + (int) this.location.getY() + "," + this.status + "," + dogOut + ",";
		} else {
		return this.id + "," + (int) this.location.getX() + "," + (int) this.location.getY() + "," + this.status + "," + dogOut + "," + this.suspectID;
		}
	}
	
	public void run() {
		switch (this.status) {
			case "Standby" :
				getSuspect();
				break;
			case "Approaching Kennel" :
				destination = k1.getLocation();
				if (moveToPoint(destination, 3)) {
					this.status = "At Kennel";
				}
				break;
			case "At Kennel" :
				if (this.returningDog) {
					k1.returnDog();
					this.dog = false;
					this.returningDog = false;
					this.station = getNearestStation();
					this.status = "Returning";
				} else {
					if (k1.getDog()) {
						this.dog = true;
						this.status = "Approaching Suspect";
					} else {
						System.out.println(this.id + " at Kennel waiting for dog");
					}
				}
				break;
			case "Approaching Suspect" :
				destination = this.crim.getLocation();
				if (moveToPoint(destination, 4)) {
					this.status = "At Scene";
				}
				break;
			case "At Scene" :
				if (this.sceneCount == 0) {
					this.returningDog = true;
					this.status = "Approaching Kennel";
					this.sceneCount = 4;
					this.crim.status = "Caught";
				} else {
					System.out.println(this.id + " at scene for " + this.sceneCount + " more seconds");
					this.sceneCount--;
				}
				break;
			case "Returning" :
				destination = this.station.getLocation();
				if (moveToPoint(destination, 3)) {
					this.status = "Standby";
					this.crim.status = "Jailed";
					this.suspectID = 0;
					this.crim.policeID = "";
				} else {
					System.out.println(this.id + " at " + this.location + " Approaching Station at " + destination);
				}
				break;
		}
		System.out.println(this.id + " at location " + this.location + " status " + this.status);
	}
	
	public void getSuspect() {
		synchronized(suspects) {
			double nearestDistance = Double.MAX_VALUE;
			Suspects nearestSuspect = null;
			double distance;
			for (Suspects suspect : this.suspects) {
				if (suspect.status.equals("Unassigned")) {
					//double distance = Math.sqrt(Math.pow((suspect.x - this.x),2) + Math.pow((suspect.y - this.y),2));
					distance =  this.location.distanceSq(suspect.getLocation());
					if (distance < nearestDistance) {
						nearestDistance = distance;
						nearestSuspect = suspect;
					}
				}
			}
			if (nearestSuspect != null) {
				nearestSuspect.status = "Assigned";
				nearestSuspect.policeID = this.id;
				this.crim = nearestSuspect;
				this.suspectID = nearestSuspect.id;
				this.status = "Approaching Kennel";
				System.out.println("Officer ID: " + this.id + " nearest suspect " + nearestSuspect.id + " at " + nearestSuspect.getLocation());
			}
			return;
		}
	}
	
	public boolean moveToPoint(Point destination, int moves) {
        while (moves > 0) {
            if (this.location.x < destination.x) {
                this.location.translate(1,0);
            } else if (this.location.x > destination.x) {
                this.location.translate(-1,0);
            } else if (this.location.y < destination.y) {
                this.location.translate(0,1);
            } else if (this.location.y > destination.y) {
                this.location.translate(0,-1);
            }
            
            if (this.location.distance(destination)==0) {
                return true;
            }
            moves--;
        }
        return false;
    }
	
	public PoliceStation getNearestStation() {
		synchronized(stations) {
			double nearestDistance = Double.MAX_VALUE;
			PoliceStation nearestStation = this.stations.get(0);
			double distance;
			for (PoliceStation station : this.stations) {
				if (station.hasRoom()) {
					//double distance = Math.sqrt(Math.pow((suspect.x - this.x),2) + Math.pow((suspect.y - this.y),2));
					distance =  this.location.distanceSq(station.getLocation());
					if (distance < nearestDistance) {
						nearestDistance = distance;
						nearestStation = station;
					}
				}
			}
			nearestStation.addTo(); //add to atomic count of officers at station
			return nearestStation;
		}
	}
	
	public String toString() {
		return this.id + " " + this.location + " " + this.status + " " + this.dog + " " + this.suspectID;
	}

}