import os
import threading
import time

from data.problem import Problem
from data.solution import Solution
from program_testing import test_program as tp

import global_app
from data import db_session
from data.user import User
from program_testing.message import get_message_solution
from program_testing.test_program import TestProgram
from utils.send_solution import send_solution


def test_checker(app):
    test_program: TestProgram = tp.get_test_program()
    thread = threading.Thread(target=test_program.start, args=(), daemon=True,
                              kwargs={'threads': app.config['TEST_THREADS']})
    thread.start()
    time.sleep(0.5)

    tests = [
        (b'''
a,b=map(int, input().split())
print(a+b)
''', 'python'),
        (b'''
var x,y: integer;

begin
   readln(x,y);
   writeln(x+y);
end.
''', 'freepascal'),
    (b'''
using System;
using System.Text;
namespace MyApplication
{
  class Program
  {
     static void Main() 
     {  Console.InputEncoding = Encoding.GetEncoding(1251); // для чтения или вывода русского текста
        Console.OutputEncoding = Encoding.GetEncoding(1251);

        int[] nums = Array.ConvertAll(Console.ReadLine().Split(' '),s=>Convert.ToInt32(s));
        Console.WriteLine((nums[0]+nums[1]).ToString());
     }
  }
}
''', 'cs'),
        (rb'''
#include <iostream>
#include <bits/stdc++.h>
using namespace std;
int main()
{ int a,b;
  ios::sync_with_stdio(0);
  cin.tie(0);
  cin>>a>>b;
  cout<<(a+b)<<"\n";
  return 0;
}
''', 'c++'),
    (rb'''
import java.util.*;
class program {
 public static Scanner in = new Scanner(System.in);
 static public void main(String []args){
    int a,b;
    a = in.nextInt(); 
    b = in.nextInt(); 
    System.out.println(a+b);
  }
}
''', 'java'),
        (b'''
import subprocess as sp
res = sp.Popen(['shutdown', '--help'], stdout=sp.PIPE, stderr=sp.PIPE).communicate()
print(res)
''', 'python'),
    ]
    for source, lang in tests:
        db_sess = db_session.create_session()
        sol = send_solution(
            db_sess.query(Problem).first().id,
            source, lang, None, db_sess.query(User).first(), db_sess)
        sol_id = sol.id

        while 1:
            time.sleep(0.5)
            db_sess = db_session.create_session()
            sol: Solution = db_sess.query(Solution).filter(Solution.id == sol_id).first()
            print(f'status ({sol.id}):', get_message_solution(sol))
            if sol.completed:
                stdin = None
                stdout = None
                stderr = None
                correct = None
                tests = TestProgram.read_tests(sol.problem)
                test_results = TestProgram.read_test_results(sol)
                tests_success = len(test_results)
                if not sol.success:
                    tests_success -= 1
                    stdin, correct = tests[len(test_results) - 1]
                    stdin = stdin
                    correct = correct
                    stdout = test_results[-1].stdout
                    stderr = test_results[-1].stderr
                    if stdout:
                        stdout = stdout
                    if stderr:
                        stderr = stderr
                print(f'''
                stdin {stdin}
                stdout {stdout}
                stderr {stderr}
                correct {correct}
                ''')

                break
