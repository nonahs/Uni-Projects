package Part1;

import java.awt.Point;
import java.util.concurrent.atomic.AtomicInteger;

public class PoliceStation {
	public String name;
	private AtomicInteger currentUnits = new AtomicInteger(0);
	private Point location;
	public int maxUnits;
	
	public PoliceStation(String name, int x, int y, int maxUnits) {
		this.name = name;
		this.location = new Point(x, y);
		this.maxUnits = maxUnits;
	}
	
	public Point getLocation() {
        return this.location;
    }
	
	public int maxUnits() {
		return this.maxUnits;
	}
	
	public boolean hasRoom() {
		if (this.currentUnits.get() < maxUnits) {
			return true;
		}
		return false;
	}
	
	
	public void addTo() {
		this.currentUnits.incrementAndGet();
	}
	
	public int currentRoom() {
		return this.currentUnits.get();
	}
	
	public String toString() {
		return this.name + " " + location + " " + this.maxUnits;
	}

}
