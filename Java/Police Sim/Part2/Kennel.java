package Part2;

import java.awt.Point;
import java.util.concurrent.atomic.AtomicInteger;

public class Kennel {
	
	private AtomicInteger numDogs;
	private Point location = new Point(50,50);
	
	public Kennel(int numDogs) {
		this.numDogs = new AtomicInteger(numDogs);
	}
	
	public Point getLocation() {
        return this.location;
    }
	
	public int currentDogs() {
		return this.numDogs.get();
	}
	
	public boolean getDog() {
		if (this.numDogs.get() > 0) {
			this.numDogs.decrementAndGet();
			return true;
		}
		return false;
	}
	
	public void returnDog() {
		this.numDogs.getAndIncrement();
	}
	
	public String toString() {
		return "Dogs in kennel: " + this.numDogs;
	}
	

}
