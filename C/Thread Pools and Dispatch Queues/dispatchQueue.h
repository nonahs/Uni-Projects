#ifndef DISPATCHQUEUE_H
#define	DISPATCHQUEUE_H

#include <pthread.h>
#include <semaphore.h>
    
#define error_exit(MESSAGE)     perror(MESSAGE), exit(EXIT_FAILURE)

    typedef enum { // whether dispatching a task synchronously or asynchronously
        ASYNC, SYNC
    } task_dispatch_type_t;
    
    typedef enum { // The type of dispatch queue.
        CONCURRENT, SERIAL
    } queue_type_t;

    typedef struct task {
        char name[64];              // to identify it when debugging
        void (*work)(void *);       // the function to perform
        void *params;               // parameters to pass to the function
        task_dispatch_type_t type;  // asynchronous or synchronous
    } task_t;
    
    typedef struct dispatch_queue_t dispatch_queue_t; // the dispatch queue type
    typedef struct dispatch_queue_thread_t dispatch_queue_thread_t; // the dispatch queue thread type
	typedef struct node node_t;

    struct dispatch_queue_thread_t {
        dispatch_queue_t *queue;// the queue this thread is associated with
        pthread_t thread;       // the thread which runs the task
        sem_t thread_semaphore; // the semaphore the thread waits on until a task is allocated
        task_t *task;           // the current task for this tread
    };

    struct dispatch_queue_t {
        queue_type_t queue_type;            // the type of queue - serial or concurrent
		pthread_t *threads;				// pointer to threads
		task_t *task_queue;			// pointer to task queue
		pthread_mutex_t queue_lock;		// lock for adding task
		pthread_cond_t notify;		// to notify threads to continue
		sem_t thread_semaphore;		// the semaphore the thread waits on until a task is allocated
		int head;					// pointer to head of queue
		int tail;					// pointer to tail of queue
		int task_amount;			// amount of tasks in the queue
		int queue_size;				// size of the queue
		int shutdown;				// let the threads know to shutdown
		int current;				// current head task
    };
	
	
	struct node {
		task_t *task;
		node_t *prev;
		node_t *next;
	};
    
    task_t *task_create(void (*)(void *), void *, char*);
    
    void task_destroy(task_t *);

    dispatch_queue_t *dispatch_queue_create(queue_type_t);
    
    void dispatch_queue_destroy(dispatch_queue_t *);
    
    void dispatch_async(dispatch_queue_t *, task_t *);
    
    void dispatch_sync(dispatch_queue_t *, task_t *);
        
    void dispatch_queue_wait(dispatch_queue_t *);
	
	void add_to_list(node_t *, task_t *);

#endif	/* DISPATCHQUEUE_H */