package Part2;

import java.awt.Point;

public class Suspects {
	private Point location;
	public int id;
	public String status;
	public String policeID = "";
	
	public Suspects (int id, int x, int y, String status) {
		this.id = id;
		this.location = new Point(x, y);
		this.status = status;
	}
	
	public Point getLocation() {
        return this.location;
    }
	
	public String returnStatus() {
		return this.id + "," + (int) this.location.getX() + "," + (int) this.location.getY() + "," + this.status + "," + this.policeID;
	}
	
	public String toString() {
		return this.id + " " + this.location + " " + this.status + " " + this.policeID;
	}

}
