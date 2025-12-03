import random
from game.room import Room

class Maze:
    def __init__(self, num_rooms=30):
        self.rooms = {}
        self.room_positions = {}  # room_id: (x, y) grid position
        self.grid = {}  # (x, y): room_id
        self.start_room_id = 0
        self.goal_room_id = num_rooms - 1
        self.generate_maze(num_rooms)
    
    def generate_maze(self, num_rooms):
        """Generate a spatially consistent maze using grid-based generation"""
        # Start at origin
        current_pos = (0, 0)
        self.room_positions[0] = current_pos
        self.grid[current_pos] = 0
        self.rooms[0] = Room(0, False)
        
        # Direction mappings
        direction_vectors = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }
        opposite = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east'
        }
        
        # Generate rooms using random walk with backtracking
        room_id = 1
        visited = [0]
        frontier = [0]  # Rooms that can be expanded from
        
        while room_id < num_rooms and frontier:
            # Pick a random room from frontier to expand from
            from_room_id = random.choice(frontier)
            from_pos = self.room_positions[from_room_id]
            
            # Find available directions
            available_dirs = []
            for direction, (dx, dy) in direction_vectors.items():
                new_pos = (from_pos[0] + dx, from_pos[1] + dy)
                # Check if this position is free
                if new_pos not in self.grid:
                    available_dirs.append((direction, new_pos))
            
            if not available_dirs:
                # No more directions from this room, remove from frontier
                frontier.remove(from_room_id)
                continue
            
            # Choose a random available direction
            direction, new_pos = random.choice(available_dirs)
            
            # Create new room
            is_goal = (room_id == self.goal_room_id)
            self.rooms[room_id] = Room(room_id, is_goal)
            self.room_positions[room_id] = new_pos
            self.grid[new_pos] = room_id
            
            # Connect the rooms bidirectionally
            self.rooms[from_room_id].add_connection(direction, room_id)
            self.rooms[room_id].add_connection(opposite[direction], from_room_id)
            
            # Add new room to frontier
            frontier.append(room_id)
            visited.append(room_id)
            
            # Occasionally add extra connections to create loops (20% chance)
            if random.random() < 0.2:
                for direction, (dx, dy) in direction_vectors.items():
                    neighbor_pos = (new_pos[0] + dx, new_pos[1] + dy)
                    if neighbor_pos in self.grid:
                        neighbor_id = self.grid[neighbor_pos]
                        # Only connect if not already connected
                        if direction not in self.rooms[room_id].connections:
                            self.rooms[room_id].add_connection(direction, neighbor_id)
                            self.rooms[neighbor_id].add_connection(opposite[direction], room_id)
                            break
            
            room_id += 1
    
    def get_room(self, room_id):
        return self.rooms.get(room_id)
