package Part2;

import java.awt.FlowLayout;

import javax.swing.JFrame;

public class SimulationFrame extends JFrame {
	
	public SimulationFrame(String name) {
		super(name);
		setLayout(new FlowLayout());
		setSize(800, 400);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
	}

}
