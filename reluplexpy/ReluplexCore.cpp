#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <map>
#include <vector>
#include <set>
#include <string>
#include <utility>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include "Reluplex.h"
#include "glpk.h"
#include "IReluplex.h"
#include "String.h"
#include "File.h"
#include <cstdio>
#include <signal.h>
#include "Set.h"


namespace py = pybind11;

int redirectOutputToFile(std::string outputFilePath){
    // Redirect standard output to a file
    int outputFile = open(outputFilePath.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if ( outputFile < 0 )
    {
        printf( "Error redirecting output to file\n");
        exit( 1 );
    }

    int outputStream = dup( STDOUT_FILENO );
    if (outputStream < 0)
    {
        printf( "Error duplicating standard output\n" );
        exit(1);
    }

    if ( dup2( outputFile, STDOUT_FILENO ) < 0 )
    {
        printf("Error duplicating to standard output\n");
        exit(1);
    }

    close( outputFile );
    return outputStream;
}

void restoreOutputStream(int outputStream)
{
    // Restore standard output
    fflush( stdout );
    if (dup2( outputStream, STDOUT_FILENO ) < 0){
        printf( "Error restoring output stream\n" );
        exit( 1 );
    }
    close(outputStream);
}
Reluplex *lastReluplex = NULL;
void got_signal( int )
{
    if ( lastReluplex )
    {
        lastReluplex->quit();
    }
}

std::pair<Reluplex::FinalStatus, std::map<int, double>> solve(Reluplex &reluplex, std::string redirect=""){
    // Arguments: Reluplex object, filename to redirect output
    // Returns: final status result, map from variable number to value
    std::map<int, double> ret;
    Reluplex::FinalStatus result = Reluplex::NOT_DONE;
    
    // Redirect file output if file given
    int output=-1;
    if(redirect.length()>0) 
    {
        output=redirectOutputToFile(redirect);
    }
    
    // Signal handling to allow graceful Ctrl+c
    lastReluplex = &reluplex;
    struct sigaction sa;
    memset( &sa, 0, sizeof(sa) );
    sa.sa_handler = got_signal;
    sigfillset( &sa.sa_mask );
    sigaction( SIGINT, &sa, NULL );
    
    // Reluplex settings before solving
    reluplex.setLogging( false );
    reluplex.setDumpStates( false );
    reluplex.toggleAlmostBrokenReluEliminiation( false );
    
    // Timer
    timeval start = Time::sampleMicro();
    timeval end;
    
    // Try to solve
    try{
        result = reluplex.solve();
        
        if ( result == Reluplex::SAT )
        {
            printf( "Solution found!\n\n" );
            for(unsigned int i=0; i<reluplex.getNumVariables(); i++)
                ret[i] = reluplex.getAssignment(i);
        }
        else if ( result == Reluplex::UNSAT )
        {
            printf( "Can't solve!\n" );
        }
        else if ( result == Reluplex::ERROR )
        {
            printf( "Reluplex error!\n" );
        }
    }
    catch(const Error  &e){
        printf( "Reluplex.cpp: Error caught. Code: %u. Errno: %i. Message: %s\n",
                e.code(),
                e.getErrno(),
                e.userMessage() );
        fflush( 0 );
    }
    
    end = Time::sampleMicro();

    unsigned milliPassed = Time::timePassed( start, end );
    unsigned seconds = milliPassed / 1000;
    unsigned minutes = seconds / 60;
    unsigned hours = minutes / 60;

    printf( "Total run time: %u milli (%02u:%02u:%02u)\n",
            Time::timePassed( start, end ), hours, minutes - ( hours * 60 ), seconds - ( minutes * 60 ) );
    
    if(output != -1)
        restoreOutputStream(output);
    
    // Reset pointer used for quitting gracefully
    lastReluplex = NULL;
    return std::make_pair(result, ret);
}

PYBIND11_MODULE(ReluplexCore, m) {
    m.doc() = "Reluplex API Library"; 
    m.def("solve", &solve, "Takes in reluplex object and returns the solution");  
    m.def("got_signal", &got_signal, "Handle Ctrl+C event");
    py::class_<IReluplex>(m, "IReluplex");
    py::class_<Reluplex, IReluplex> reluplex(m, "Reluplex");
    reluplex.def(py::init<unsigned>())
        .def("setUpperBound", &Reluplex::setUpperBound)
        .def("setLowerBound", &Reluplex::setLowerBound)
        .def("getUpperBound", &Reluplex::getUpperBound)
        .def("getLowerBound", &Reluplex::getLowerBound)
        .def("getNumberOfVariables", &Reluplex::getNumVariables)
        .def("initializeCell", &Reluplex::initializeCell)
        .def("setReluPair", &Reluplex::setReluPair)
        .def("markBasic", &Reluplex::markBasic);
    py::enum_<Reluplex::FinalStatus>(reluplex, "FinalStatus")
        .value("SAT", Reluplex::FinalStatus::SAT)
        .value("UNSAT", Reluplex::FinalStatus::UNSAT)
        .value("ERROR", Reluplex::FinalStatus::ERROR)
        .value("NOT_DONE", Reluplex::FinalStatus::NOT_DONE)
        .export_values();
}
